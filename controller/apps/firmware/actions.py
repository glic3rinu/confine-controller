from __future__ import absolute_import

from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

from controller.utils.plugins.actions import sync_plugins_action

from .exceptions import ConcurrencyError
from .forms import BaseImageForm, OptionalFilesForm, RegistryApiForm
from .models import BaseImage, Build, Config


@transaction.atomic
def get_firmware(modeladmin, request, queryset):
    if queryset.count() != 1:
        messages.warning(request, "One node at a time")
        return
    
    opts = modeladmin.model._meta
    app_label = opts.app_label
    site_name = modeladmin.admin_site.name
    
    node = queryset.get()
    config = get_object_or_404(Config)
    base_images = config.get_images(node)
    
    # Check if the user has permissions for download the image
    if not request.user.has_perm('nodes.getfirmware_node', node):
        raise PermissionDenied
    
    # Hack for allowing calling this action from node changelist
    if request.path == reverse('admin:nodes_node_changelist'):
        return redirect('admin:nodes_node_firmware', node.pk)
    
    node_url = reverse("admin:nodes_node_change", args=[node.pk])
    node_link = '<a href="%s">%s</a>' % (node_url, node)

    # Initialize plugin instances and hook node
    plugins = config.plugins.active()
    for plugin in plugins:
        if plugin.instance.form is not None:
            setattr(plugin.instance.form, 'node', node)
    
    context = {
        "title": "Download firmware for your research device %s" % node,
        "content_title":  mark_safe("Download firmware for research device %s" % node_link),
        "content_message": "Please, choose the base image which you want to get the firmware.",
        "action_name": 'Firmware',
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'node': node,
        'img_form': BaseImageForm(arch=node.arch),
        'opt_form': OptionalFilesForm(prefix='opt'),
        'api_form': RegistryApiForm(prefix='api'),
        'plugins': plugins,
    }
    
    # No architecture support
    if not base_images.exists():
        msg = "Sorry but currently we do not support %s architectures :(" % node.arch
        context["content_message"] = msg
        template = 'admin/firmware/base_build.html'
        return TemplateResponse(request, template, context, current_app=site_name)
    
    # process the form
    if request.method == 'POST':
        # plugins
        kwargs = {}
        all_valid = True
        for plugin in context['plugins']:
            if plugin.instance.form:
                form = plugin.instance.form(request.POST)
                plugin.instance.form = form
                if form.is_valid():
                    kwargs.update(plugin.instance.process_form_post(form))
                else:
                    all_valid = False
        
        # base image and optional files forms
        img_form = BaseImageForm(data=request.POST, arch=node.arch)
        opt_form = OptionalFilesForm(request.POST, prefix='opt')
        api_form = RegistryApiForm(request.POST, prefix='api')
        
        # validate every form to get possible errors
        img_form_valid = img_form.is_valid() 
        opt_form_valid = opt_form.is_valid()
        api_form_valid = api_form.is_valid()
        if all_valid and img_form_valid and opt_form_valid and api_form_valid:
            # provide ServerApi data to firmware generator (base_uri + cert)
            # - base_uri will be handled by Config UCI
            # - cert will be writed in a Config File
            kwargs['registry_base_uri'] = api_form.cleaned_data['base_uri']
            kwargs['registry_cert'] = api_form.cleaned_data['cert']
            
            base_image = img_form.cleaned_data['base_image']
            optional_fields = opt_form.cleaned_data
            exclude = [ field for field, value in optional_fields.iteritems() if not value ]
            try:
                build = Build.build(node, base_image, async=True, exclude=exclude, **kwargs)
            except ConcurrencyError as e:
                # handle a duplicate build request but keep request
                # as progress bar or download page will be shown.
                messages.error(request, e.message)
            else:
                modeladmin.log_change(request, node, "Build firmware")
        else:
            # Display form validation errors
            context['img_form'] = img_form
            context['opt_form'] = opt_form
            context['api_form'] = api_form
            template = 'admin/firmware/generate_build.html'
            return TemplateResponse(request, template, context, current_app=site_name)
    
    try:
        build = Build.objects.get_current(node=node)
    except Build.DoesNotExist:
        state = False
    else:
        state = build.state
    
    # Build a new firmware
    if not state or state in [Build.DELETED, Build.FAILED]:
        title = "Generate firmware for research device %s" % node_link
        if state == Build.FAILED:
            msg = ("<b>The last build for this research device has failed</b>. "
                   "This problem has been reported to the operators, but you can "
                   "try to build again the image")
        else:
            msg = ("There is no pre-build up-to-date firmware for this research "
                   "device, but you can instruct the system to build a fresh one "
                   "for you, it will take only a few seconds.")
        context["content_message"] = mark_safe(msg)
        context["content_title"] = mark_safe(title)
        template = 'admin/firmware/generate_build.html'
        return TemplateResponse(request, template, context, current_app=site_name)
    
    context.update({
        "content_message": build.state_description,
        "build": build, })
    
    # Available for download
    if state in [Build.AVAILABLE, Build.OUTDATED]:
        # avoid circular imports
        from .admin import STATE_COLORS
        context['state_color'] = STATE_COLORS[state]
        try:
            context['base_image'] = base_images.get(image=build.base_image)
        except BaseImage.DoesNotExist:
            context['base_image'] = build.base_image
        template = 'admin/firmware/download_build.html'
        return TemplateResponse(request, template, context, current_app=site_name)
    
    # Processing
    title = "Generating firmware for research device %s ..." % node_link
    context["content_title"] = mark_safe(title)
    template = 'admin/firmware/processing_build.html'
    return TemplateResponse(request, template, context, current_app=modeladmin.admin_site.name)
get_firmware.short_description = ugettext_lazy("Get firmware for selected %(verbose_name)s")
get_firmware.url_name = 'firmware'
get_firmware.verbose_name = u'Download firmware\u2026'
get_firmware.css_class = 'viewsitelink'
get_firmware.description = mark_safe('Build and download a customized firmware for this node.')


sync_plugins = sync_plugins_action('firmwareplugins')
sync_plugins.verbose_name = 'Sync plugins'

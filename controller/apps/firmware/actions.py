from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import router, transaction
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

from .exceptions import BaseImageNotAvailable
from .forms import OptionalFilesForm
from .models import Build, Config


@transaction.commit_on_success
def get_firmware(modeladmin, request, queryset):
    if queryset.count() != 1:
        messages.warning(request, "One node at a time")
        return
    
    opts = modeladmin.model._meta
    app_label = opts.app_label
    site_name = modeladmin.admin_site.name
    
    using = router.db_for_write(modeladmin.model)
    node = queryset.get()
    
    # Check if the user has permissions for download the image
    if not request.user.has_perm('nodes.getfirmware_node', node):
        raise PermissionDenied
    
    config = Config.objects.get()
    node_url = reverse("admin:nodes_node_change", args=[node.pk])
    node_link = '<a href="%s">%s</a>' % (node_url, node)
    
    context = {
        "title": "Download firmware for your research device %s" % node,
        "content_title":  mark_safe("Download firmware for your research device %s" % node_link),
        "action_name": 'Firmware',
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'node': node,
        'form': OptionalFilesForm(),
        'plugins': config.plugins.filter(is_active=True)
    }

    # No architecture support
    try:
        config.get_image(node)
    except BaseImageNotAvailable:
        context["content_message"] = "Sorry but currently we do not support \
                                      %s architectures :(" % node.arch
        template = 'admin/firmware/base_build.html'
        return TemplateResponse(request, template, context, current_app=site_name)
    
    # User has requested a firmware build
    if request.POST.get('post'):
        form = OptionalFilesForm(request.POST)
        if form.is_valid():
            optional_fields = form.cleaned_data
            exclude = [ field for field, value in optional_fields.iteritems() if not value ]
            build = Build.build(node, async=True, exclude=exclude)
            modeladmin.log_change(request, node, "Build firmware")
    
    try:
        build = Build.objects.get_current(node=node)
    except Build.DoesNotExist:
        state = False
    else:
        state = build.state
    
    # Build a new firmware
    if not state or state in [Build.DELETED, Build.OUTDATED, Build.FAILED]:
        if state == Build.FAILED:
            msg = ("<b>The last build for this research device has failed</b>. "
                   "This problem has been reported to the operators, but you can "
                   "try to build again the image")
        else:
            msg = ("There is no pre-build up-to-date firmware for this research "
                   "device, but you can instruct the system to build a fresh one "
                   "for you, it will take only a few seconds.")
        context["content_message"] = mark_safe(msg)
        template = 'admin/firmware/generate_build.html'
        return TemplateResponse(request, template, context, current_app=site_name)
    
    context.update({
        "content_message": build.state_description,
        "build": build,
    })
    
    # Available for download
    if state in [Build.AVAILABLE]:
        template = 'admin/firmware/download_build.html'
        return TemplateResponse(request, template, context, current_app=site_name)
    
    # Processing
    template = 'admin/firmware/processing_build.html'
    return TemplateResponse(request, template, context, current_app=modeladmin.admin_site.name)

get_firmware.short_description = ugettext_lazy("Get firmware for selected %(verbose_name)s")
get_firmware.url_name = 'firmware'
get_firmware.verbose_name = 'Download Firmware'
get_firmware.css_class = 'viewsitelink'

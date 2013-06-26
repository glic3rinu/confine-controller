from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import router, transaction
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

from firmware.forms import BaseImageForm
from firmware.models import BaseImage


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
    base_images = BaseImage.objects.filter_by_arch(node.arch)
    
    # Check if the user has permissions for download the image
    if not request.user.has_perm('nodes.getfirmware_node', node):
        raise PermissionDenied
    
    node_url = reverse("admin:nodes_node_change", args=[node.pk])
    node_link = '<a href="%s">%s</a>' % (node_url, node)
    
    context = {
        "title": "Download firmware for your research device %s" % node,
        "content_title":  mark_safe("Download firmware for your research device %s" % node_link),
        "content_message": "Please, choose the base image which you want to get the firmware.",
        "action_name": 'Firmware',
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'node': node,
        'form': BaseImageForm(arch=node.arch),
    }
    
    if request.method == 'POST':
        form = BaseImageForm(data=request.POST, arch=node.arch)
        if form.is_valid():
            base_image = form.cleaned_data['base_image']
            return redirect('admin:nodes_node_firmware_get', node.pk, base_image.pk)
        else:
            # update context with current form for display errors 
            context['form'] = form
    
    # No architecture support
    if base_images.count() == 0:
        msg = "Sorry but currently we do not support %s architectures :(" % node.arch
        context["content_message"] = msg
        template = 'admin/firmware/base_build.html'
        return TemplateResponse(request, template, context, current_app=site_name)
    
    # Only one base image, redirect to next step
    #elif base_images.count() == 1:
    #    base_image = base_images[0]
    #    return redirect('admin:nodes_node_firmware_get', node.id, base_image.id)
    
    # Show form for choosing the base image
    template = 'admin/firmware/select_base_image.html'
    return TemplateResponse(request, template, context, current_app=modeladmin.admin_site.name)

get_firmware.short_description = ugettext_lazy("Get firmware for selected %(verbose_name)s")
get_firmware.url_name = 'firmware'
get_firmware.verbose_name = 'Download Firmware'
get_firmware.css_class = 'viewsitelink'

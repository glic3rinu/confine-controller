from celery.result import AsyncResult
from django.contrib.admin import helpers
from django.core.urlresolvers import reverse
from django.db import router, transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import simplejson
from django.utils.safestring import mark_safe

from controller.admin.utils import get_modeladmin
from nodes.models import Node

from firmware.exceptions import BaseImageNotAvailable
from firmware.forms import OptionalFilesForm
from firmware.models import BaseImage, Build, Config


def build_info_view(request, node_id, bimg_id):
    """ Hook JSON representation of a Build to NodeModeladmin """
    base_image = get_object_or_404(BaseImage, pk=bimg_id)
    try:
        build = Build.objects.get(node=node_id)
    except Build.DoesNotExist:
        info = {}
    else:
        task = AsyncResult(build.task_id)
        result = task.result or {}
        state = build.state
        if state in [Build.REQUESTED, Build.QUEUED, Build.BUILDING]:
            state = 'PROCESS'
        info = {
            'state': state,
            'progress': result.get('progress', 0),
            'next': result.get('next', 0),
            'description': "%s ..." % result.get('description', 'Waiting for your build task to begin.'),
            'id': build.pk,
            'content_message': build.state_description }
    return HttpResponse(simplejson.dumps(info), mimetype="application/json")


@transaction.commit_on_success
def delete_build_view(request, node_id, bimg_id):
    """ View for deleting a firmware build (with confirmation) """
    node = get_object_or_404(Node, pk=node_id)
    base_image = get_object_or_404(BaseImage, pk=bimg_id)
    build = get_object_or_404(Build, node=node)
    
    # Check that the user has delete permission for the actual model
    node_modeladmin = get_modeladmin(Node)
    if not node_modeladmin.has_change_permission(request, obj=node, view=False):
        raise PermissionDenied
    
    # The user has already confirmed the deletion.
    if request.POST.get('post'):
        build.delete()
        node_modeladmin.log_change(request, node, "Deleted firmware build")
        node_modeladmin.message_user(request, "Firmware build has been successfully deleted.")
        return redirect('admin:nodes_node_firmware_get', node_id, bimg_id)
    
    context = {
        'opts': node_modeladmin.model._meta,
        'app_label': node_modeladmin.model._meta.app_label,
        'title': 'Are your sure?',
        'build': build,
        'base_image': base_image,
        'node': node, }
    return render(request, 'admin/firmware/delete_build_confirmation.html', context)


def get_firmware_view(request, node_id, bimg_id):
    """ Build or download node firmware """
    modeladmin = get_modeladmin(Node)
    node = get_object_or_404(Node, pk=node_id)
    base_image = get_object_or_404(BaseImage, pk=bimg_id)
    config = Config.objects.get()
    
    opts = modeladmin.model._meta
    app_label = opts.app_label
    site_name = modeladmin.admin_site.name
    using = router.db_for_write(modeladmin.model)
    
    # Check if the user has permissions for download the image
    if not request.user.has_perm('nodes.getfirmware_node', node):
        raise PermissionDenied
    
    node_url = reverse("admin:nodes_node_change", args=[node.pk])
    node_link = '<a href="%s">%s</a>' % (node_url, node)
    
    context = {
        "title": "Download firmware for your research device %s" % node,
        "content_title":  mark_safe("Download firmware for your research device %s (%s)" % (node_link, base_image.name)),
        "action_name": 'Firmware',
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'node': node,
        'base_image': base_image,
        'form': OptionalFilesForm(),
        'plugins': config.plugins.active(),
    }

    # No architecture support
#    try:
#        Config.objects.get().get_image(node, base_image)
#    except BaseImageNotAvailable:
#        context["content_message"] = "Sorry but currently we do not support \
#                                      %s architectures :(" % node.arch
#        template = 'admin/firmware/base_build.html'
#        return TemplateResponse(request, template, context, current_app=site_name)

    # User has requested a firmware build
    if request.POST.get('post'):
        kwargs = {}
        all_valid = True
        for plugin in context['plugins']:
            form = plugin.instance.form(request.POST)
            plugin.instance.form = form
            if form.is_valid():
                kwargs.update(plugin.instance.process_form_post(form))
            else:
                all_valid = False
        form = OptionalFilesForm(request.POST)
        if all_valid and form.is_valid():
            optional_fields = form.cleaned_data
            exclude = [ field for field, value in optional_fields.iteritems() if not value ]
            build = Build.build(node, base_image, async=True, exclude=exclude, **kwargs)
            modeladmin.log_change(request, node, "Build firmware")
        else:
            # Display form validation errors
            template = 'admin/firmware/generate_build.html'
            return TemplateResponse(request, template, context, current_app=site_name)
    
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

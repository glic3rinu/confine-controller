import json

from celery.result import AsyncResult
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from controller.admin.utils import get_modeladmin
from nodes.models import Node

from firmware.models import Build


def build_info_view(request, node_id):
    """ Hook JSON representation of a Build to NodeModeladmin """
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
    return HttpResponse(json.dumps(info), content_type="application/json")


@transaction.atomic
def delete_build_view(request, node_id):
    """ View for deleting a firmware build (with confirmation) """
    node = get_object_or_404(Node, pk=node_id)
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
        return redirect('admin:nodes_node_firmware', node_id)
    
    context = {
        'opts': node_modeladmin.model._meta,
        'app_label': node_modeladmin.model._meta.app_label,
        'title': 'Are your sure?',
        'build': build,
        'node': node, }
    return render(request, 'admin/firmware/delete_build_confirmation.html', context)

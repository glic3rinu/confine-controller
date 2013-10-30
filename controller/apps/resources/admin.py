from django.contrib import admin

from controller.admin.utils import insertattr
from nodes.models import Node
from permissions.admin import PermissionGenericTabularInline

from .models import Resource, ResourceReq


class ResourceAdmin(PermissionGenericTabularInline):
    fields = ['name', 'max_sliver', 'dflt_sliver', 'unit']
    readonly_fields = ['unit']
    model = Resource


class ResourceReqAdmin(PermissionGenericTabularInline):
    fields = ['name', 'req', 'unit']
    readonly_fields = ['unit']
    model = ResourceReq


insertattr(Node, 'inlines', ResourceAdmin)

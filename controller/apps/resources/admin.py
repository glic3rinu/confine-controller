from django.contrib import admin

from controller.admin.utils import insertattr
from controller.forms.widgets import ShowText
from nodes.models import Node
from permissions.admin import PermissionGenericTabularInline

from . import ResourcePlugin
from .forms import ResourceInlineFormSet
from .models import Resource, ResourceReq


class ResourceAdminInline(PermissionGenericTabularInline):
    fields = ['name', 'max_sliver', 'dflt_sliver', 'unit']
    readonly_fields = ['unit']
    model = Resource
    formset = ResourceInlineFormSet
    extra = 0
    can_delete = False
    
    def get_max_num(self, request, obj=None, **kwargs):
        """Hook for customizing the max number of extra inline forms."""
        return len(ResourcePlugin.get_resources_for_producer(type(self.parent_model)))
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'name':
            kwargs['widget'] = ShowText
        return super(ResourceAdminInline, self).formfield_for_dbfield(db_field, **kwargs)


class ResourceReqAdminInline(PermissionGenericTabularInline):
    fields = ['name', 'req', 'unit']
    readonly_fields = ['unit']
    model = ResourceReq
    extra = 0
    
    def get_max_num(self, request, obj=None, **kwargs):
        """Hook for customizing the max number of extra inline forms."""
        return len(ResourcePlugin.get_resources_for_consumer(type(self.parent_model)))


for producer_model in ResourcePlugin.get_producers_model():
    insertattr(producer_model, 'inlines', ResourceAdminInline)

for consumer_model in ResourcePlugin.get_consumers_model():
    insertattr(consumer_model, 'inlines', ResourceReqAdminInline)

from __future__ import absolute_import

from controller.admin.utils import insertattr
from permissions.admin import PermissionGenericTabularInline

from . import ResourcePlugin
from .forms import (ResourceInlineFormSet, ResourceReqInlineFormSet,
    ResourceReqForm, VerboseNameShowTextWidget)
from .models import Resource, ResourceReq


class ResourceAdminInline(PermissionGenericTabularInline):
    fields = ['name', 'unit', 'max_req', 'dflt_req', 'avail']
    readonly_fields = ['unit', 'avail']
    model = Resource
    formset = ResourceInlineFormSet
    extra = 0
    max_num = 0
    can_delete = False
    
    class Media:
        js = ('resources/js/collapsed_resources.js',)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Readonly resource name but form input still hidden """
        if db_field.name == 'name':
            kwargs['widget'] = VerboseNameShowTextWidget()
        return super(ResourceAdminInline, self).formfield_for_dbfield(db_field, **kwargs)



class ResourceReqAdminInline(PermissionGenericTabularInline):
    fields = ['name', 'unit', 'req']
    readonly_fields = ['unit']
    model = ResourceReq
    max_num = 0
    form = ResourceReqForm
    formset = ResourceReqInlineFormSet
    can_delete = False
    
    class Media:
        css = {
            "all": ("resources/css/resource-admin.css",)
        }
        js = ('resources/js/collapsed_resource_requests.js',)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Readonly resource name but form input still hidden """
        if db_field.name == 'name':
            kwargs['widget'] = VerboseNameShowTextWidget()
        return super(ResourceReqAdminInline, self).formfield_for_dbfield(db_field, **kwargs)
    
    def get_readonly_fields(self, request, obj=None):
        """
        Remove 'name' from readonly fields because its value
        is required to call properly Resource.get
        ResourceReqForm is in charge of mark it as readonly.
        
        """
        ro_fields = super(ResourceReqAdminInline, self).get_readonly_fields(request, obj=obj)
        if 'name' in ro_fields:
            ro_fields.remove('name')
        return ro_fields


for producer_model in ResourcePlugin.get_producers_models():
    insertattr(producer_model, 'inlines', ResourceAdminInline)

from slices.admin import SliceSliversAdmin
for consumer_model in list(ResourcePlugin.get_consumers_models()) + [SliceSliversAdmin]:
    insertattr(consumer_model, 'inlines', ResourceReqAdminInline, weight=-1)

from django import forms
from django.contrib import admin

from controller.admin.utils import insertattr
from controller.forms.widgets import ShowText
from permissions.admin import PermissionGenericTabularInline

from . import ResourcePlugin
from .forms import (ResourceInlineFormSet, ResourceReqInlineFormSet,
    ResourceReqForm, VerboseNameShowTextWidget)
from .models import Resource, ResourceReq


class ResourceAdminInline(PermissionGenericTabularInline):
    fields = ['name', 'unit', 'dflt_sliver', 'max_sliver']
    readonly_fields = ['unit']
    model = Resource
    formset = ResourceInlineFormSet
    extra = 0
    max_num = 0
    can_delete = False
    
    class Media:
        js = ('resources/js/collapsed_resources.js',)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Readonly resource name but form intput still hidden """
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
        js = ('resources/js/collapsed_resource_requests.js',)


for producer_model in ResourcePlugin.get_producers_models():
    insertattr(producer_model, 'inlines', ResourceAdminInline)

from slices.admin import SliceSliversAdmin
for consumer_model in list(ResourcePlugin.get_consumers_models()) + [SliceSliversAdmin]:
    insertattr(consumer_model, 'inlines', ResourceReqAdminInline, weight=-1)

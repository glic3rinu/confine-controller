from django import forms
from django.contrib import admin

from controller.admin.utils import insertattr
from controller.forms.widgets import ShowText
from nodes.models import Node
from permissions.admin import PermissionGenericTabularInline

from . import ResourcePlugin
from .forms import ResourceInlineFormSet, VerboseNameShowTextWidget, ResourceReqInlineForm
from .models import Resource, ResourceReq


class ResourceAdminInline(PermissionGenericTabularInline):
    fields = ['name', 'max_sliver', 'dflt_sliver', 'unit']
    readonly_fields = ['unit']
    model = Resource
    formset = ResourceInlineFormSet
    extra = 0
    max_num = 0
    can_delete = False
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Readonly resource name but form intput still hidden """
        if db_field.name == 'name':
            kwargs['widget'] = VerboseNameShowTextWidget()
        return super(ResourceAdminInline, self).formfield_for_dbfield(db_field, **kwargs)


class ResourceReqAdminInline(PermissionGenericTabularInline):
    fields = ['name', 'req', 'unit']
    readonly_fields = ['unit']
    model = ResourceReq
    extra = 0
    form = ResourceReqInlineForm
    
    def get_max_num(self, request, obj=None, **kwargs):
        """Hook for customizing the max number of extra inline forms."""
        return len(ResourcePlugin.get_resources_for_consumer(type(self.parent_model)))

    def get_formset(self, request, obj=None, **kwargs):
        """ Hook node for future usage in the inline form """
        self.form.parent_model = self.parent_model
        return super(ResourceReqAdminInline, self).get_formset(request, obj=obj, **kwargs)


for producer_model in ResourcePlugin.get_producers_models():
    insertattr(producer_model, 'inlines', ResourceAdminInline)

for consumer_model in ResourcePlugin.get_consumers_models():
    insertattr(consumer_model, 'inlines', ResourceReqAdminInline)

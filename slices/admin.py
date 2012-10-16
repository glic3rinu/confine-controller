from common.admin import ChangeViewActionsMixin
from django.contrib import admin
from slices.actions import renew_selected_slices, reset_selected_slices, reset_selected_slivers
from slices.forms import SliverInlineAdminForm
from slices.models import (Sliver, SliverProp, IsolatedIface, PublicIface, 
    PrivateIface, Slice, SliceProp, Template)


class SliverPropInline(admin.TabularInline):
    model = SliverProp
    extra = 0


class IsolatedIfaceInline(admin.TabularInline):
    model = IsolatedIface
    extra = 0


class PublicIfaceInline(admin.TabularInline):
    model = PublicIface
    extra = 0


class PrivateIfaceInline(admin.TabularInline):
    model = PrivateIface
    extra = 0


class SliverAdmin(ChangeViewActionsMixin):
    list_display = ['description', 'id', 'instance_sn', 'node', 'slice']
    list_filter = ['slice__name']
    readonly_fields = ['instance_sn']
    search_fields = ['description', 'node__description', 'slice__name']
    inlines = [SliverPropInline, IsolatedIfaceInline, PublicIfaceInline, 
               PrivateIfaceInline]
    actions = [reset_selected_slivers]

    def reset_sliver_view(self, request, object_id):
        return action_as_view(reset_selected_slivers, self, request, object_id)


class SliverInline(admin.TabularInline):
    model = Sliver
    form = SliverInlineAdminForm
    max_num = 0
    readonly_fields = ['instance_sn']


class SlicePropInline(admin.TabularInline):
    model = SliceProp
    extra = 0


class SliceAdmin(ChangeViewActionsMixin):
    list_display = ['name', 'uuid', 'instance_sn', 'vlan_nr', 'set_state',
        'template', 'expires_on']
    list_filter = ['set_state']
    readonly_fields = ['instance_sn', 'new_sliver_instance_sn', 'expires_on']
    date_hierarchy = 'expires_on'
    search_fields = ['name', 'uuid']
    inlines = [SlicePropInline,SliverInline]
    actions = [reset_selected_slices, renew_selected_slices]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', ('template', 'exp_data'), 
                       'vlan_nr', 'set_state', 'users', 'instance_sn', 
                       'new_sliver_instance_sn', 'expires_on'),
        }),
        ('Public key', {
            'classes': ('collapse',),
            'fields': ('pubkey',)
        }),)
    change_form_template = "admin/slices/slice/change_form.html"
    change_view_actions = [('renew', renew_selected_slices, 'Renew', ''),
                           ('reset', reset_selected_slices, 'Reset', '') ]

    def renew_slice_view(self, request, object_id):
        return action_as_view(renew_selected_slices, self, request, object_id)

    def reset_slice_view(self, request, object_id):
        return action_as_view(reset_selected_slices, self, request, object_id)


class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'type', 'arch', 'data', 'is_active']
    list_filter = ['is_active', 'type', 'arch']
    search_fields = ['name', 'description', 'type', 'arch']


admin.site.register(Sliver, SliverAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(Template, TemplateAdmin)

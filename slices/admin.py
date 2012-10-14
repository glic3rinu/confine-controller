from django.contrib import admin
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


class SliverAdmin(admin.ModelAdmin):
    list_display = ['description', 'id', 'instance_sn', 'node', 'slice']
    list_filter = ['slice__name']
    readonly_fields = ['instance_sn']
    search_fields = ['description', 'node__description', 'slice__name']
    inlines = [SliverPropInline, IsolatedIfaceInline, PublicIfaceInline, 
               PrivateIfaceInline]


class SliverInline(admin.TabularInline):
    model = Sliver
    form = SliverInlineAdminForm
    max_num = 0
    readonly_fields = ['instance_sn']


class SlicePropInline(admin.TabularInline):
    model = SliceProp
    extra = 0


class SliceAdmin(admin.ModelAdmin):
    list_display = ['name', 'uuid', 'instance_sn', 'vlan_nr', 'set_state',
        'template', 'expires_on']
    list_filter = ['set_state']
    readonly_fields = ['instance_sn', 'new_sliver_instance_sn']
    date_hierarchy = 'expires_on'
    search_fields = ['name', 'uuid']
    inlines = [SlicePropInline,SliverInline]


class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'type', 'arch', 'data', 'is_active']
    list_filter = ['is_active', 'type', 'arch']
    search_fields = ['name', 'description', 'type', 'arch']


admin.site.register(Sliver, SliverAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(Template, TemplateAdmin)

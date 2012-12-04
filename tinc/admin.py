from __future__ import absolute_import

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.contenttypes import generic

from common.admin import (insert_inline, admin_link, insert_action, 
    get_modeladmin, ChangeViewActionsModelAdmin, link)
from nodes.models import Node, Server
from permissions.admin import (PermissionGenericTabularInline, PermissionTabularInline,
    PermissionModelAdmin)

from .actions import set_island
from .filters import MyHostsListFilter
from .forms import HostInlineAdminForm
from .models import Host, TincClient, TincAddress, TincServer, Island, Gateway


class TincClientInline(PermissionGenericTabularInline):
    model = TincClient
    max_num = 1
    readonly_fields = ['connect_to', 'subnet']
    verbose_name_plural = 'Tinc client'


class TincServerInline(PermissionGenericTabularInline):
    # TODO TincAddress nested inlines: https://code.djangoproject.com/ticket/9025
    model = TincServer
    max_num = 1
    verbose_name_plural = 'Tinc server'
    readonly_fields = ['subnet']


class TincAddressInline(PermissionTabularInline):
    model = TincAddress
    max_num = 1
    verbose_name_plural = 'Tinc address'


class ReadOnlyTincAddressInline(PermissionTabularInline):
    model = TincAddress
    readonly_fields = ['ip_addr', 'port', 'server']
    can_delete = False
    max_num = 0


class TincAddressAdmin(PermissionModelAdmin):
    list_display = ['ip_addr', 'port', 'island', 'server']
    list_filter = ['island__name', 'port', 'server']
    search_fields = ['ip_addr', 'island__name', 'island__description', 
                     'server__tinc_name'] 


class IslandAdmin(PermissionModelAdmin):
    list_display = ['name', 'id', 'description']
    search_fields = ['name', 'description']
    inlines = [ReadOnlyTincAddressInline]


class GatewayAdmin(PermissionModelAdmin):
    list_display = ['id']
    inlines = [TincServerInline]


class HostAdmin(ChangeViewActionsModelAdmin, PermissionModelAdmin):
    list_display = ['description', 'id', admin_link('admin'), 'subnet']
    inlines = [TincClientInline]
    actions = [set_island]
    list_filter = [MyHostsListFilter]
    change_view_actions = [('set-island', set_island, 'Set Island', ''),]
    change_form_template = "admin/common/change_form.html"
    
    def subnet(self, instance):
        return instance.tinc.subnet
    subnet.admin_order_field = 'id'
    
    def get_form(self, request, *args, **kwargs):
        """ request.user as default host admin """
        form = super(HostAdmin, self).get_form(request, *args, **kwargs)
        if 'admin' in form.base_fields:
            # ronly forms doesn't have initial
            form.base_fields['admin'].initial = request.user
        return form
    
    def set_island_view(modeladmin, request, object_id):
        return action_as_view(set_island, modeladmin, request, object_id)


admin.site.register(Host, HostAdmin)
admin.site.register(TincAddress, TincAddressAdmin)
admin.site.register(Island, IslandAdmin)
admin.site.register(Gateway, GatewayAdmin)


# Monkey-Patching Section

insert_inline(Node, TincClientInline)
insert_inline(Server, TincServerInline)
insert_action(Node, set_island)

node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action('set-island', set_island, 'Set Island', '')


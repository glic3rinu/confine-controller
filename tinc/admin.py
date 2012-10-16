from common.admin import (insert_inline, admin_link, insert_action, get_modeladmin, 
    action_as_view, DynamicChangeViewLinksMixin)
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from nodes.models import Node, Server
from tinc.actions import set_island
from tinc.forms import HostInlineAdminForm
from tinc.models import Host, TincClient, TincAddress, TincServer, Island, Gateway


class TincClientInline(generic.GenericTabularInline):
    model = TincClient
    max_num = 1
    readonly_fields = ['connect_to']


class TincServerInline(admin.TabularInline):
    model = TincServer
    max_num = 1


class TincAddressInline(admin.TabularInline):
    model = TincAddress
    max_num = 1


class TincAddressAdmin(admin.ModelAdmin):
    list_display = ['ip_addr', 'port', 'island', 'server']
    list_filter = ['island__name', 'port', 'server']
    search_fields = ['ip_addr', 'island__name', 'island__description', 
                     'server__tinc_name'] 


class IslandAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'description']
    search_fields = ['name', 'description']
    inlines = [TincAddressInline]


class GatewayAdmin(admin.ModelAdmin):
#    list_display = ['tinc_name', 'id' ]
    inlines = [TincServerInline]


class HostAdmin(DynamicChangeViewLinksMixin):
    list_display = ['description', 'id', admin_link('admin')]
    inlines = [TincClientInline]
    actions = [set_island]
    change_view_links = [('set-island', 'set_island_view', 'Set Island', ''),]
    
    def get_form(self, request, *args, **kwargs):
        """ request.user as default host admin """
        form = super(HostAdmin, self).get_form(request, *args, **kwargs)
        form.base_fields['admin'].initial = request.user
        return form

    def set_island_view(modeladmin, request, object_id):
        return action_as_view(set_island, modeladmin, request, object_id)


admin.site.register(Host, HostAdmin)
admin.site.register(TincAddress, TincAddressAdmin)
admin.site.register(Island, IslandAdmin)
admin.site.register(Gateway, GatewayAdmin)


class HostInline(admin.TabularInline):
    model = Host
    form = HostInlineAdminForm
    max_num = 0


insert_inline(User, HostInline)
insert_inline(Node, TincClientInline)
insert_inline(Server, TincClientInline)
insert_action(Node, set_island)


# FIXME set_island_view() takes exactly 3 non-keyword arguments (1 given)
def set_island_view(modeladmin, request, object_id):
    return action_as_view(set_island, modeladmin, request, object_id)

node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_link('set-island', set_island_view, 'Set Island', '')

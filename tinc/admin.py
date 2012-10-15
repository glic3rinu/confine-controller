from common.admin import insert_inline, admin_link, insert_action, get_modeladmin
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from nodes.models import Node, Server
from tinc.actions import set_islands
from tinc.forms import HostInlineAdminForm
from tinc.models import Host, TincClient, TincAddress, TincServer, Island, Gateway


class TincClientInline(generic.GenericTabularInline):
    model = TincClient
    max_num = 1
    readonly_fields = ['connect_to']


class TincServerInline(admin.TabularInline):
    model = TincServer
    max_num = 1


class TincAddressAdmin(admin.ModelAdmin):
    list_display = ['ip_addr', 'port', 'island', 'server']
    list_filter = ['island__name', 'port', 'server']
    search_fields = ['ip_addr', 'island__name', 'island__description', 
                     'server__tinc_name'] 


class IslandAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'description']
    search_fields = ['name', 'description']


class GatewayAdmin(admin.ModelAdmin):
#    list_display = ['tinc_name', 'id' ]
    inlines = [TincServerInline]


class HostAdmin(admin.ModelAdmin):
    list_display = ['description', 'id', admin_link('admin')]
    inlines = [TincClientInline]
    actions = [set_islands]


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
insert_action(Node, set_islands)


def set_island_view(modeladmin, request, object_id):
    pass

node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_link('set-island', set_island_view, 'Set Island', '')

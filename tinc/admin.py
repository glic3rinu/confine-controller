from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.contenttypes import generic

from common.admin import (insert_inline, admin_link, insert_action, 
    get_modeladmin, ChangeViewActionsModelAdmin, link)
from nodes.models import Node, Server
#from users.admin import PermExtensionMixin

from .actions import set_island
from .forms import HostInlineAdminForm
from .models import Host, TincClient, TincAddress, TincServer, Island, Gateway


class TincClientInline(generic.GenericTabularInline):
    model = TincClient
    max_num = 1
    readonly_fields = ['connect_to']
    verbose_name_plural = 'Tinc client'


class TincServerInline(generic.GenericTabularInline):
    # TODO TincAddress nested inlines: https://code.djangoproject.com/ticket/9025
    model = TincServer
    max_num = 1
    verbose_name_plural = 'Tinc server'


class TincAddressInline(admin.TabularInline):
    model = TincAddress
    max_num = 1
    verbose_name_plural = 'Tinc address'


class ReadOnlyTincAddressInline(admin.TabularInline):
    model = TincAddress
    readonly_fields = ['ip_addr', 'port', 'server']
    can_delete = False
    max_num = 0


class TincAddressAdmin(admin.ModelAdmin):
    list_display = ['ip_addr', 'port', 'island', 'server']
    list_filter = ['island__name', 'port', 'server']
    search_fields = ['ip_addr', 'island__name', 'island__description', 
                     'server__tinc_name'] 


class IslandAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'description']
    search_fields = ['name', 'description']
    inlines = [ReadOnlyTincAddressInline]


class GatewayAdmin(admin.ModelAdmin):
    list_display = ['id']
    inlines = [TincServerInline]


class HostAdmin(ChangeViewActionsModelAdmin):
    list_display = ['description', 'id', admin_link('admin')]
    inlines = [TincClientInline]
    actions = [set_island]
    change_view_actions = [('set-island', set_island, 'Set Island', ''),]
    
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


# Monkey-Patching Section

class HostInline(admin.TabularInline):
    model = Host
    form = HostInlineAdminForm
    max_num = 0

#insert_inline(get_user_model(), HostInline)
insert_inline(Node, TincClientInline)
insert_inline(Server, TincServerInline)
insert_action(Node, set_island)

node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action('set-island', set_island, 'Set Island', '')


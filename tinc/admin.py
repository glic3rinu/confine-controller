from common.admin import insert_inline, admin_link
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from nodes.models import ResearchDevice, Server
from tinc.forms import HostInlineAdminForm
from tinc.models import Host, TincClient, TincAddress, Island, Gateway


class TincClientInline(generic.GenericTabularInline):
    model = TincClient
    max_num = 1


class TincAddressAdmin(admin.ModelAdmin):
    list_display = ['ip_addr', 'port', 'island', 'server']
    list_filter = ['island__name', 'port']
    search_fields = ['ip_addr', 'island__name', 'island__description', 'server__tinc_name'] 


class IslandAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'description']
    search_fields = ['name', 'description']


class GatewayAdmin(admin.ModelAdmin):
    list_display = ['tinc_name', 'id' ]


class HostAdmin(admin.ModelAdmin):
    list_display = ['description', 'id', admin_link('admin')]
    inlines = [TincClientInline]


admin.site.register(Host, HostAdmin)
admin.site.register(TincAddress, TincAddressAdmin)
admin.site.register(Island, IslandAdmin)
admin.site.register(Gateway, GatewayAdmin)


class HostInline(admin.TabularInline):
    model = Host
    form = HostInlineAdminForm
    max_num = 0


insert_inline(User, HostInline)
insert_inline(ResearchDevice, TincClientInline)
insert_inline(Server, TincClientInline)

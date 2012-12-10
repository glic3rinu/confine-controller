from __future__ import absolute_import

from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.contenttypes import generic
from django.template.response import TemplateResponse

from common.admin import (insert_inline, admin_link, insert_action, wrap_admin_view,
    get_modeladmin, ChangeViewActionsModelAdmin, link)
from common.forms import RequiredGenericInlineFormSet
from common.widgets import ReadOnlyWidget
from nodes.models import Node, Server
from permissions.admin import (PermissionGenericTabularInline, PermissionTabularInline,
    PermissionModelAdmin)

from .actions import set_island
from .filters import MyHostsListFilter
from .forms import HostInlineAdminForm
from .models import Host, TincClient, TincAddress, TincServer, Island, Gateway
from . import settings


class TincClientInline(PermissionGenericTabularInline):
    model = TincClient
    max_num = 1
    readonly_fields = ['connect_to', 'address']
    verbose_name_plural = 'Tinc client'
    formset = RequiredGenericInlineFormSet


class TincServerInline(PermissionGenericTabularInline):
    # TODO TincAddress nested inlines: https://code.djangoproject.com/ticket/9025
    model = TincServer
    max_num = 1
    verbose_name_plural = 'Tinc server'
    readonly_fields = ['address']


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
    list_display = ['description', 'id', admin_link('admin'), 'address']
    inlines = [TincClientInline]
    actions = [set_island]
    list_filter = [MyHostsListFilter]
    change_view_actions = [('set-island', set_island, 'Set Island', ''),]
    change_form_template = "admin/tinc/host/change_form.html"
    
    def address(self, instance):
        return instance.tinc.address if instance.tinc else ''
    address.admin_order_field = 'id'
    
    def get_urls(self):
        urls = super(HostAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        extra_urls = patterns("", 
            url("^(?P<host_id>\d+)/help", wrap_admin_view(self, self.help_view), name='host-help'),
        )
        return extra_urls + urls
    
    def help_view(self, request, host_id):
        host = self.get_object(request, host_id)
        opts = self.model._meta
        context = {'host': host,
                   'server': Server.objects.get(),
                   'net_name': settings.TINC_NET_NAME,
                   'opts': opts,
                   'app_label': opts.app_label}
        return TemplateResponse(request, 'admin/tinc/host/help.html', context, 
                                current_app=self.admin_site.name)
    
    def get_form(self, request, *args, **kwargs):
        """ request.user as default host admin """
        form = super(HostAdmin, self).get_form(request, *args, **kwargs)
        if 'admin' in form.base_fields:
            # ronly forms doesn't have initial
            user = request.user
            if not user.is_superuser:
                form.base_fields['admin'].widget = ReadOnlyWidget(user.id, user.username)
                form.base_fields['admin'].required = False
            else:
                form.base_fields['admin'].initial = user
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


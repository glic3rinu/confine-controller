from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.template.response import TemplateResponse

from controller.admin import ChangeViewActionsModelAdmin 
from controller.admin.utils import (insert_inline, admin_link, insert_action,
    get_modeladmin, link, wrap_admin_view,)
from controller.forms.widgets import ReadOnlyWidget
from nodes.models import Node, Server
from permissions.admin import (PermissionGenericTabularInline, PermissionTabularInline,
    PermissionModelAdmin)

from .filters import MyHostsListFilter
from .forms import HostInlineAdminForm
from .models import Host, TincClient, TincAddress, TincServer, Island, Gateway
from . import settings


class TincClientInline(PermissionGenericTabularInline):
    model = TincClient
    max_num = 1
    readonly_fields = ['tinc_compatible_address']
    verbose_name_plural = 'Tinc client'
    
    def tinc_compatible_address(self, instance):
        """ return instance.address in a format compatible with tinc daemon """
        return instance.address.strNormal()
    tinc_compatible_address.short_description = 'Address'
    
    def get_readonly_fields(self, request, obj=None):
        """ pubkey as readonly if exists """
        readonly_fields = super(TincClientInline, self).get_readonly_fields(request, obj=obj)
        if obj and obj.tinc.pubkey and 'pubkey' not in readonly_fields:
            return ['pubkey'] + readonly_fields
        return readonly_fields
    
    def get_fieldsets(self, request, obj=None):
        """ Warning user if the tinc client is not fully configured """
        if obj and not obj.tinc.pubkey:
            messages.warning(request, 'This %s misses a tinc public key.' % obj._meta.verbose_name)
        return super(TincClientInline, self).get_fieldsets(request, obj=obj)


class TincServerInline(PermissionGenericTabularInline):
    # TODO TincAddress nested inlines: https://code.djangoproject.com/ticket/9025
    # TODO warn user when it tries to modify a tincserver with depends on more than 
    #      one client without alternative path
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
    readonly_fields = ['addr', 'port', 'server']
    can_delete = False
    max_num = 0


class TincAddressAdmin(PermissionModelAdmin):
    list_display = ['addr', 'port', 'island', 'server']
    list_filter = ['island__name', 'port', 'server']
    search_fields = ['addr', 'island__name', 'island__description', 'server__tinc_name']


class IslandAdmin(PermissionModelAdmin):
    list_display = ['name', 'id', 'description']
    search_fields = ['name', 'description']
    inlines = [ReadOnlyTincAddressInline]


class GatewayAdmin(PermissionModelAdmin):
    list_display = ['id', 'description']
    list_display_links = ['id', 'description']
    inlines = [TincServerInline]


class HostAdmin(PermissionModelAdmin):
    list_display = ['description', 'id', admin_link('owner'), 'address']
    inlines = [TincClientInline]
    list_filter = [MyHostsListFilter]
    change_form_template = "admin/tinc/host/change_form.html"
    
    def address(self, instance):
        return instance.tinc.address if instance.tinc else ''
    address.admin_order_field = 'id'
    
    def get_urls(self):
        urls = super(HostAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        extra_urls = patterns("", 
            url("^(?P<host_id>\d+)/help",
                wrap_admin_view(self, self.help_view),
                name='host-help'),
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
        if 'owner' in form.base_fields:
            # ronly forms doesn't have initial
            user = request.user
            if not user.is_superuser:
                ro_widget = ReadOnlyWidget(user.id, user.username)
                form.base_fields['owner'].widget = ro_widget
                form.base_fields['owner'].required = False
            else:
                form.base_fields['owner'].initial = user
        return form
    
    def changelist_view(self, request, extra_context=None):
        """ Default filter as 'my_hosts=True' """
        if not request.GET.has_key('my_hosts'):
            q = request.GET.copy()
            q['my_hosts'] = 'True'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(HostAdmin,self).changelist_view(request, extra_context=extra_context)


admin.site.register(Host, HostAdmin)
admin.site.register(TincAddress, TincAddressAdmin)
admin.site.register(Island, IslandAdmin)
admin.site.register(Gateway, GatewayAdmin)


# Monkey-Patching Section

insert_inline(Node, TincClientInline)
insert_inline(Server, TincServerInline)

node_modeladmin = get_modeladmin(Node)

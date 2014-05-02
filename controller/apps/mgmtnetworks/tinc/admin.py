from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from controller.admin import ChangeListDefaultFilter
from controller.admin.utils import (get_modeladmin, insertattr, admin_link,
    wrap_admin_view)
from controller.forms.widgets import ReadOnlyWidget
from nodes.models import Island, Node, Server
from permissions.admin import (PermissionGenericTabularInline, PermissionTabularInline,
    PermissionModelAdmin)

from .filters import MyHostsListFilter
from .forms import TincClientInlineForm, TincServerInlineForm
from .models import Host, TincClient, TincAddress, TincServer, Gateway
from . import settings


class TincHostInline(PermissionGenericTabularInline):
    fields = ['pubkey', 'clear_pubkey', 'tinc_compatible_address']
    readonly_fields = ['tinc_compatible_address']
    model = TincClient
    max_num = 1
    can_delete = False
    
    class Media:
        css = {
             'all': (
                'tinc/monospace-pubkey.css',
                'controller/css/hide-inline-id.css')
        }
    
    def tinc_compatible_address(self, instance):
        """ return instance.address in a format compatible with tinc daemon """
        return instance.address.strNormal()
    tinc_compatible_address.short_description = 'Address'
    
    def get_readonly_fields(self, request, obj=None):
        """ pubkey as readonly if exists """
        readonly_fields = super(TincHostInline, self).get_readonly_fields(request, obj=obj)
        if obj and obj.tinc.pubkey and 'pubkey' not in readonly_fields:
            return ['pubkey'] + readonly_fields
        return readonly_fields
    
    def get_formset(self, request, obj=None, **kwargs):
        """ Warning user if the tinc host is not fully configured """
        if obj and not obj.tinc.pubkey and request.method == 'GET':
            msg = 'This %s misses a tinc public key.' % obj._meta.verbose_name
            messages.warning(request, msg)
        return super(TincHostInline, self).get_formset(request, obj=obj, **kwargs)


class TincClientInline(TincHostInline):
    model = TincClient
    verbose_name_plural = 'tinc client'
    form = TincClientInlineForm


class TincServerInline(TincHostInline):
    # TODO TincAddress nested inlines: https://code.djangoproject.com/ticket/9025
    # TODO warn user when it tries to modify a tincserver with depends on more than 
    #      one client without alternative path
    fields = ['pubkey', 'clear_pubkey', 'tinc_compatible_address', 'is_active']
    model = TincServer
    verbose_name_plural = 'tinc server'
    form = TincServerInlineForm


class TincAddressInline(PermissionTabularInline):
    model = TincAddress
    max_num = 1
    verbose_name_plural = 'tinc address'


class ReadOnlyTincAddressInline(PermissionTabularInline):
    model = TincAddress
    readonly_fields = ['addr', 'port', 'server']
    can_delete = False
    max_num = 0


class TincAddressAdmin(PermissionModelAdmin):
    list_display = ['addr', 'port', 'island', 'server']
    list_filter = ['island__name', 'port', 'server']
    search_fields = ['addr', 'island__name', 'island__description', 'server__tinc_name']


class GatewayAdmin(PermissionModelAdmin):
    list_display = ['id', 'description']
    list_display_links = ['id', 'description']
    inlines = [TincServerInline]


class HostAdmin(ChangeListDefaultFilter, PermissionModelAdmin):
    list_display = ['description', 'id', admin_link('owner'), 'address', 'island']
    inlines = [TincClientInline]
    list_filter = [MyHostsListFilter]
    change_form_template = "admin/tinc/host/change_form.html"
    save_and_continue = True
    default_changelist_filters = (('my_hosts', 'True'),)
    
    def address(self, instance):
        return instance.tinc.address if instance.tinc else ''
    address.admin_order_field = 'id'
    
    def get_urls(self):
        urls = super(HostAdmin, self).get_urls()
        extra_urls = patterns("", 
            url("^(?P<host_id>\d+)/help",
                wrap_admin_view(self, self.help_view),
                name='host-help'),
        )
        return extra_urls + urls
    
    def help_view(self, request, host_id):
        host = get_object_or_404(Host, pk=host_id)
        opts = self.model._meta
        context = {
            'host': host,
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
                ro_widget = ReadOnlyWidget(user.id, user.get_username())
                form.base_fields['owner'].widget = ro_widget
                form.base_fields['owner'].required = False
            else:
                form.base_fields['owner'].initial = user
        return form
    
    def queryset(self, request):
        """ Prevent regular users to see hosts from other users """
        qset = super(HostAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qset
        return qset.filter(owner=request.user)


admin.site.register(Host, HostAdmin)
admin.site.register(TincAddress, TincAddressAdmin)
admin.site.register(Gateway, GatewayAdmin)


# Monkey-Patching Section

insertattr(Node, 'inlines', TincClientInline, weight=-5)
insertattr(Server, 'inlines', TincServerInline)
insertattr(Island, 'inlines', ReadOnlyTincAddressInline)

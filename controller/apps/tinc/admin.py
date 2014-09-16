from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from controller.admin import ChangeListDefaultFilter
from controller.admin.utils import insertattr, admin_link, wrap_admin_view
from controller.forms.widgets import ReadOnlyWidget
from mgmtnetworks.admin import MgmtNetConfInline
from nodes.models import Island, Node, Server
from permissions.admin import (PermissionGenericTabularInline, PermissionTabularInline,
    PermissionModelAdmin)

from .filters import MyHostsListFilter
from .forms import TincHostInlineForm
from .models import Host, TincHost, TincAddress, Gateway
from . import settings


class TincHostInline(PermissionGenericTabularInline):
    # TODO TincAddress nested inlines: https://code.djangoproject.com/ticket/9025
    # TODO warn user when it tries to modify a tinchost with depends on more than 
    #      one client without alternative path
    fields = ['pubkey', 'clear_pubkey']
    model = TincHost
    form = TincHostInlineForm
    max_num = 1
    can_delete = False
    verbose_name = 'tinc configuration'
    verbose_name_plural = 'tinc configuration'
    
    class Media:
        css = {
             'all': (
                'tinc/monospace-pubkey.css',
                'controller/css/hide-inline-id.css')
        }
    
    def get_readonly_fields(self, request, obj=None):
        """ pubkey as readonly if exists """
        readonly_fields = super(TincHostInline, self).get_readonly_fields(request, obj=obj)
        if obj and obj.tinc.pubkey and 'pubkey' not in readonly_fields:
            return ('pubkey',) + readonly_fields
        return readonly_fields
    
    def get_formset(self, request, obj=None, **kwargs):
        """ Warning user if the tinc host is not fully configured """
        if (obj and obj.mgmt_net.backend == 'tinc' and obj.tinc.pubkey is None and
            request.method == 'GET'):
            msg = 'This %s misses a tinc public key ' % obj._meta.verbose_name
            if obj._meta.verbose_name == 'node':
                msg += '(will be automatically generated during firmware build).'
            messages.warning(request, msg)
        return super(TincHostInline, self).get_formset(request, obj=obj, **kwargs)


class TincAddressInline(PermissionTabularInline):
    model = TincAddress
    max_num = 1
    verbose_name_plural = 'tinc address'


class ReadOnlyTincAddressInline(PermissionTabularInline):
    model = TincAddress
    readonly_fields = ['addr', 'port', 'host']
    can_delete = False
    max_num = 0


class TincAddressAdmin(PermissionModelAdmin):
    list_display = ['addr', 'port', 'island', 'host']
    list_filter = ['island__name', 'port', 'host']
    search_fields = ['addr', 'island__name', 'island__description', 'host__tinc_name']


class GatewayAdmin(PermissionModelAdmin):
    list_display = ['id', 'description']
    list_display_links = ['id', 'description']
    inlines = [MgmtNetConfInline, TincHostInline]


class HostAdmin(ChangeListDefaultFilter, PermissionModelAdmin):
    list_display = ['id', 'name', 'description', admin_link('owner'),
        'address', admin_link('island')]
    list_display_links = ['id', 'name']
    inlines = [MgmtNetConfInline, TincHostInline]
    list_filter = [MyHostsListFilter]
    change_form_template = "admin/tinc/host/change_form.html"
    save_and_continue = True
    default_changelist_filters = (('my_hosts', 'True'),)
    
    def address(self, instance):
        return instance.mgmt_net.addr
    address.admin_order_field = 'id'

    def display_description(self, instance):
        return instance.description or None
    display_description.verbose_name = 'description'
    display_description.admin_order_field = 'description'
    
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

insertattr(Node, 'inlines', TincHostInline, weight=-5)
insertattr(Server, 'inlines', TincHostInline)
insertattr(Island, 'inlines', ReadOnlyTincAddressInline)

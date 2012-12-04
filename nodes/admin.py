from __future__ import absolute_import

from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import transaction, models
from django.db.models import Q
from singleton_models.admin import SingletonModelAdmin

from common.admin import (link, insert_inline, colored, ChangeViewActionsModelAdmin,
    admin_link)
from permissions.admin import PermissionModelAdmin, PermissionTabularInline

from .actions import request_cert, reboot_selected
from .filters import MyNodesListFilter
from .forms import NodeInlineAdminForm
from .models import Node, NodeProp, Server, DirectIface


STATES_COLORS = { 
    Node.INSTALL_CONF: 'black',
    Node.INSTALL_CERT: 'grey',
    Node.DEBUG: 'darkorange',
    Node.FAILURE: 'red',
    Node.SAFE: 'grey',
    Node.PRODUCTION: 'green', }


class NodePropInline(PermissionTabularInline):
    model = NodeProp
    extra = 0


class DirectIfaceInline(PermissionTabularInline):
    model = DirectIface
    extra = 0


class NodeAdmin(ChangeViewActionsModelAdmin, PermissionModelAdmin):
    list_display = ['name', 'id', 'uuid', 'arch', colored('set_state', STATES_COLORS, verbose=True), 
                    admin_link('group'), 'num_ifaces']
    list_display_links = ('id', 'uuid', 'name')
    list_filter = [MyNodesListFilter, 'arch', 'set_state']
    search_fields = ['description', 'name', 'id', 'uuid']
    readonly_fields = ['boot_sn']
    inlines = [NodePropInline, DirectIfaceInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'group', 'arch', 'local_iface', 
                       'sliver_pub_ipv6', 'sliver_pub_ipv4', 
                       'sliver_pub_ipv4_range', 'boot_sn', 'set_state',),
        }),
        ('SFA', {
            'classes': ('collapse',),
            'fields': ('pubkey', 'cert', 'uuid')
        }),
        ('Optional Prefixes', {
            'classes': ('collapse',),
            'fields': ('priv_ipv4_prefix', 'sliver_mac_prefix')
        }),)
    actions = [request_cert, reboot_selected]
    change_view_actions = [('reboot', reboot_selected, '', ''),
                           ('request-cert', request_cert, 'Request Certificate', ''),]
    change_form_template = "admin/common/change_form.html"
    
    def num_ifaces(self, node):
        return node.directiface_set.count()
    num_ifaces.short_description = 'Ifaces'
    num_ifaces.admin_order_field = 'directiface__count'
    
    def get_form(self, request, *args, **kwargs):
        """ request.user as default node admin """
        form = super(NodeAdmin, self).get_form(request, *args, **kwargs)
        if 'group' in form.base_fields:
            # ronly forms doesn't have initial nor queryset
            user = request.user
            groups = user.groups.filter(Q(roles__is_admin=True)|Q(roles__is_technician=True))
            num_groups = groups.count()
            if num_groups >= 1:
                form.base_fields['group'].queryset = groups
            if num_groups == 1:
                form.base_fields['group'].initial = groups[0]
        return form
    
    def queryset(self, request):
        qs = super(NodeAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('directiface'))
        return qs


class ServerAdmin(ChangeViewActionsModelAdmin, SingletonModelAdmin):
    fields = []
    
    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        urlpatterns = patterns('',
            url(r'^(?P<object_id>\d+)/history/$', 
                self.history_view,
                name='%s_%s_history' % info),
            url(r'^(?P<object_id>\d+)/delete/$', 
                self.delete_view, 
                name='%s_%s_delete' % info),
            url(r'^(?P<object_id>\d+)$',
                self.change_view, 
                name='%s_%s_change' % info),
            url(r'^$',
                self.change_view, {'object_id': '1'}, 
                name='%s_%s_changelist' % info),
        )
        urls = super(ServerAdmin, self).get_urls()
        return urlpatterns + urls


admin.site.register(Node, NodeAdmin)
admin.site.register(Server, ServerAdmin)


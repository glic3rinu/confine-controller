from __future__ import absolute_import

from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe
from singleton_models.admin import SingletonModelAdmin

from controller.admin import ChangeViewActions, ChangeListDefaultFilter
from controller.admin.utils import (colored, admin_link, wrap_admin_view,
    docstring_as_help_tip, monospace_format)
from permissions.admin import PermissionModelAdmin, PermissionTabularInline
from users.helpers import filter_group_queryset

from nodes.actions import request_cert, reboot_selected
from nodes.filters import MyNodesListFilter
from nodes.forms import DirectIfaceInlineFormSet
from nodes.models import Node, NodeProp, Server, DirectIface


STATES_COLORS = {
    Node.DEBUG: 'darkorange',
    Node.FAILURE: 'red',
    Node.SAFE: 'grey',
    Node.PRODUCTION: 'green', }


class NodePropInline(PermissionTabularInline):
    model = NodeProp
    extra = 0
    verbose_name_plural = mark_safe('Node properties %s' % docstring_as_help_tip(NodeProp))


class DirectIfaceInline(PermissionTabularInline):
    model = DirectIface
    extra = 1
    formset = DirectIfaceInlineFormSet


class NodeAdmin(ChangeViewActions, ChangeListDefaultFilter, PermissionModelAdmin):
    list_display = ['name', 'id', 'arch', colored('set_state', STATES_COLORS, verbose=True, bold=False),
                    admin_link('group'), 'num_ifaces']
    list_display_links = ['name', 'id']
    list_filter = [MyNodesListFilter, 'arch', 'set_state']
    default_changelist_filters = (('my_nodes', 'True'),)
    search_fields = ['description', 'name']
    readonly_fields = ['boot_sn', 'display_cert']
    inlines = [DirectIfaceInline, NodePropInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'group', 'arch', 'set_state'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('sliver_pub_ipv4', 'sliver_pub_ipv4_range', 'local_iface',
                       'display_cert', 'priv_ipv4_prefix', 'sliver_mac_prefix',
                       'sliver_pub_ipv6', 'boot_sn')
        }), 
        )
    actions = [request_cert, reboot_selected]
    change_view_actions = [reboot_selected, request_cert]
    change_form_template = "admin/controller/change_form.html"
    
    def display_cert(self, node):
        """ Display certificate with some contextual help if cert is not present """
        if not node.pk:
            return "Certificates can be requested once the node is saved for the first time."
        if not node.cert:
            req_url = reverse('admin:nodes_node_request-cert', args=[node.pk])
            return mark_safe("<a href='%s'>Request certificate</a>" % req_url)
        return monospace_format(node.cert)
    display_cert.short_description = 'Certificate'
    
    def num_ifaces(self, node):
        """ Diplay number of direct ifaces, used on changelist """
        return node.direct_ifaces.count()
    num_ifaces.short_description = 'Ifaces'
    num_ifaces.admin_order_field = 'direct_ifaces__count'
    
    def get_form(self, request, obj=None, *args, **kwargs):
        """ request.user as default node admin """
        form = super(NodeAdmin, self).get_form(request, obj=obj, *args, **kwargs)
        if 'group' in form.base_fields:
            # ronly forms doesn't have initial nor queryset
            user = request.user
            query = Q( Q(users__roles__is_admin=True) | Q(users__roles__is_technician=True) )
            query = Q( query & Q(allow_nodes=True) )
            form = filter_group_queryset(form, obj, request.user, query)
        return form
    
    def queryset(self, request):
        """ Annotate direct iface counter to allow ordering on change list """
        qs = super(NodeAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('direct_ifaces', distinct=True))
        return qs
    
    def get_readonly_fields(self, request, obj=None):
        """ Disable set_state transitions when state is DEBUG """
        readonly_fields = super(NodeAdmin, self).get_readonly_fields(request, obj=obj)
        if 'set_state' not in readonly_fields:
            if obj is None or obj.set_state == obj.DEBUG:
                return readonly_fields + ['set_state']
        return readonly_fields
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Remove DEBUG from set_state choices, DEBUG is an automatic state """
        if db_field.name == 'description':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 85, 'rows': 5})
        field = super(NodeAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'set_state':
            # Removing Debug from choices
            assert field.choices.pop(0)[0] == Node.DEBUG, "Problem removing DEBUG from set_state"
        return field
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Warning user if the node is not fully configured """
        if request.method == 'GET':
            obj = self.get_object(request, object_id)
            if obj and not obj.cert:
                messages.warning(request, 'This node lacks a valid certificate.')
        return super(NodeAdmin, self).change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)


class ServerAdmin(ChangeViewActions, SingletonModelAdmin, PermissionModelAdmin):
    change_form_template = 'admin/nodes/server/change_form.html'
    
    def get_urls(self):
        """ Make urls singleton aware """
        info = self.model._meta.app_label, self.model._meta.module_name
        urlpatterns = patterns('',
            url(r'^(?P<object_id>\d+)/history/$',
                wrap_admin_view(self, self.history_view),
                name='%s_%s_history' % info),
            url(r'^(?P<object_id>\d+)/delete/$',
                wrap_admin_view(self, self.delete_view),
                name='%s_%s_delete' % info),
            url(r'^(?P<object_id>\d+)$',
                wrap_admin_view(self, self.change_view),
                name='%s_%s_change' % info),
            url(r'^$',
                wrap_admin_view(self, self.change_view),
                {'object_id': '1'},
                name='%s_%s_change' % info),
            url(r'^$',
                wrap_admin_view(self, self.change_view),
                {'object_id': '1'},
                name='%s_%s_changelist' % info),
        )
        urls = super(ServerAdmin, self).get_urls()
        return urlpatterns + urls
    
    def has_delete_permission(self, *args, **kwargs):
        """ It doesn't make sense to delete the server """
        return False


admin.site.register(Node, NodeAdmin)
admin.site.register(Server, ServerAdmin)

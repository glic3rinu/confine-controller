from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import transaction, models
from django.db.models import Q
from django.utils.safestring import mark_safe
from singleton_models.admin import SingletonModelAdmin

from common.admin import (link, insert_inline, colored, ChangeViewActionsModelAdmin,
    admin_link, docstring_as_help_tip)
from common.widgets import ReadOnlyWidget
from permissions.admin import PermissionModelAdmin, PermissionTabularInline

from .actions import request_cert, reboot_selected
from .filters import MyNodesListFilter
from .forms import NodeInlineAdminForm
from .models import Node, NodeProp, Server, DirectIface


STATES_COLORS = {
    Node.DEBUG: 'darkorange',
    Node.FAILURE: 'red',
    Node.SAFE: 'grey',
    Node.PRODUCTION: 'green', }


class NodePropInline(PermissionTabularInline):
    model = NodeProp
    extra = 0
    verbose_name_plural = mark_safe('Node Properties %s' % docstring_as_help_tip(NodeProp))


class DirectIfaceInline(PermissionTabularInline):
    model = DirectIface
    extra = 0


class NodeAdmin(ChangeViewActionsModelAdmin, PermissionModelAdmin):
    list_display = ['name', 'id', 'arch', colored('set_state', STATES_COLORS, verbose=True),
                    admin_link('group'), 'num_ifaces']
    list_display_links = ('id', 'name')
    list_filter = [MyNodesListFilter, 'arch', 'set_state']
    search_fields = ['description', 'name', 'id']
    readonly_fields = ['boot_sn', 'display_cert']
    inlines = [NodePropInline, DirectIfaceInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'group', 'arch', 'local_iface',
                       'sliver_pub_ipv6', 'sliver_pub_ipv4',
                       'sliver_pub_ipv4_range', 'boot_sn', 'set_state'),
        }),
        ('Certificate', {
            'classes': ('collapse',),
            'fields': ('display_cert',)
        }),
        ('Optional Prefixes', {
            'classes': ('collapse',),
            'fields': ('priv_ipv4_prefix', 'sliver_mac_prefix')
        }),)
    actions = [request_cert, reboot_selected]
    change_view_actions = [('reboot', reboot_selected, '', ''),
                           ('request-cert', request_cert, 'Request Certificate', ''),]
    change_form_template = "admin/common/change_form.html"
    
    def display_cert(self, node):
        """ Display certificate with some contextual help if cert is not present """
        if not node.pk:
            return "You will be able to request a certificate once the node is registred"
        if not node.cert:
            req_url = reverse('admin:nodes_node_request-cert', args=[node.pk])
            return mark_safe("<a href='%s'>Request certificate</a>" % req_url)
        return node.cert
    display_cert.short_description = 'Certificate'
    
    def num_ifaces(self, node):
        """ Diplay number of direct ifaces, used on changelist """
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
                ro_widget = ReadOnlyWidget(groups[0].id, groups[0].name)
                form.base_fields['group'].widget = ro_widget
                form.base_fields['group'].required = False
        return form
    
    def queryset(self, request):
        """ Annotate direct iface counter to allow ordering on change list """
        qs = super(NodeAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('directiface', distinct=True))
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
        field = super(NodeAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'set_state':
            # Removing Debug from choices
            assert field.choices.pop(0)[0] == Node.DEBUG, "Problem removing DEBUG from set_state"
        return field
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Warning user if the node is not fully configured """
        if request.method != 'POST':
            obj = self.get_object(request, object_id)
            if not obj.cert:
                messages.warning(request, 'This node lacks a valid certificate.')
        return super(NodeAdmin, self).change_view(request, object_id, form_url=form_url,
                                                  extra_context=extra_context)
    
    def changelist_view(self, request, extra_context=None):
        """ Default filter as 'my_nodes=True' """
        if not request.GET.has_key('my_nodes'):
            q = request.GET.copy()
            q['my_nodes'] = 'True'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(NodeAdmin,self).changelist_view(request, extra_context=extra_context)


class ServerAdmin(ChangeViewActionsModelAdmin, SingletonModelAdmin, PermissionModelAdmin):
    def get_urls(self):
        """ Make urls singleton aware """
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

from __future__ import absolute_import

from django import forms
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe

from controller.admin import ChangeViewActions, ChangeListDefaultFilter
from controller.admin.utils import colored, admin_link, docstring_as_help_tip
from controller.core.exceptions import InvalidMgmtAddress
from controller.models.utils import get_help_text
from controller.utils.html import monospace_format
from controller.utils.singletons.admin import SingletonModelAdmin
from permissions.admin import PermissionModelAdmin, PermissionTabularInline
from users.helpers import filter_group_queryset

from .actions import request_cert, reboot_selected
from .filters import MyNodesListFilter
from .forms import DirectIfaceInlineFormSet
from .models import DirectIface, Island, Node, NodeProp, Server, ServerProp
from .utils import get_mgmt_backend_class


STATES_COLORS = {
    Node.DEBUG: 'darkorange',
    Node.FAILURE: 'red',
    Node.SAFE: 'blue',
    Node.PRODUCTION: 'green',
}


class NodePropInline(PermissionTabularInline):
    model = NodeProp
    extra = 1
    verbose_name_plural = mark_safe('Node properties %s' % docstring_as_help_tip(NodeProp))
    
    class Media:
        js = ('nodes/js/collapsed_node_properties.js',)


class DirectIfaceInline(PermissionTabularInline):
    model = DirectIface
    extra = 1
    formset = DirectIfaceInlineFormSet


class NodeAdmin(ChangeViewActions, ChangeListDefaultFilter, PermissionModelAdmin):
    list_display = [
        'name', 'id', 'arch', 'display_set_state', admin_link('group'),
        'num_ifaces', admin_link('island')
    ]
    list_display_links = ['name', 'id']
    list_filter = [MyNodesListFilter, 'arch', 'set_state', 'group']
    default_changelist_filters = (('my_nodes', 'True'),)
    search_fields = ['description', 'name', 'id']
    readonly_fields = ['boot_sn', 'display_cert']
    inlines = [DirectIfaceInline, NodePropInline]
    weights = {
        'inlines': {
            NodePropInline: 2
        }
    }
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'group', 'set_state', 'island'),
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('arch', 'display_cert', 'boot_sn')
        }),
        ('Firmware configuration', {
            'classes': ('collapse', 'warning'),
            'description': '<strong>WARNING:</strong> Applying some changes may '\
                           'be dificult, especially if it has deployed slivers. '\
                           'Node may choose ignore those changes until it is '\
                           'rebooted. As side effect, those changes may also '\
                           'cause some slivers to be undeployed.',
            'fields': ('sliver_pub_ipv4', 'sliver_pub_ipv4_range', 'local_iface',
                       'priv_ipv4_prefix','sliver_mac_prefix', 'sliver_pub_ipv6')
        }),
    )
    actions = [request_cert, reboot_selected]
    change_view_actions = [reboot_selected, request_cert]
    change_form_template = "admin/controller/change_form.html"
    
    class Media:
        css = {
             'all': ('nodes/css/nodes-admin.css',)
        }
        js = ("nodes/js/nodes-admin.js",)
    
    def display_set_state(self, node):
        return colored('set_state', STATES_COLORS, verbose=True, bold=False)(node)
    display_set_state.short_description = 'Set state'
    display_set_state.admin_order_field = 'set_state'
    
    def display_cert(self, node):
        """ Display certificate with some contextual help if cert is not present """
        if not node.pk:
            return "Certificates can be requested once the node is saved for the first time."
        if not node.cert:
            req_url = reverse('admin:nodes_node_request-cert', args=[node.pk])
            return mark_safe("<a href='%s'>Request certificate</a>" % req_url)
        return monospace_format(node.cert)
    display_cert.short_description = 'Certificate'
    display_cert.help_text = get_help_text(Node, 'cert')
    
    def num_ifaces(self, node):
        """ Display number of direct ifaces, used on changelist """
        return node.direct_ifaces.count()
    num_ifaces.short_description = 'Ifaces'
    num_ifaces.admin_order_field = 'direct_ifaces__count'
    
    def lookup_allowed(self, key, value):
        if key in ('slivers__slice',):
            return True
        return super(NodeAdmin, self).lookup_allowed(key, value)
    
    def get_form(self, request, obj=None, *args, **kwargs):
        """ request.user as default node admin """
        form = super(NodeAdmin, self).get_form(request, obj=obj, *args, **kwargs)
        if 'group' in form.base_fields:
            # ronly forms doesn't have initial nor queryset
            is_group_admin = Q(users__roles__is_group_admin=True)
            is_node_admin = Q(users__roles__is_node_admin=True)
            query = Q( is_group_admin | is_node_admin )
            query = Q( query & Q(allow_nodes=True) )
            form = filter_group_queryset(form, obj, request.user, query)
        if (obj is not None and obj.set_state == obj.FAILURE and
            'set_state' in form.base_fields):
            # removing production choice if in failure state, only for users
            # with change permissions
            is_production = form.base_fields['set_state'].choices.pop(1)[0] == Node.PRODUCTION
            assert is_production, "Problem removing PRODUCTION from set_state"
        return form
    
    def queryset(self, request):
        """
        Annotate direct iface and slivers counter to allow ordering
        on change list. Intercept search query to allow search nodes
        by management network IP
        """
        qs = super(NodeAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('direct_ifaces', distinct=True))
        # FIXME: try to move to slices to avoid coupling nodes with slices app
        qs = qs.annotate(models.Count('slivers', distinct=True))
        # HACK for searching nodes by IP
        search = request.GET.get('q', False)
        if search:
            for query in search.split(' '):
                mgmt_backend = get_mgmt_backend_class()
                try:
                    node = mgmt_backend.reverse(query)
                except InvalidMgmtAddress:
                    pass
                else:
                    # Skip django admin filtering
                    request.GET._mutable = True
                    request.GET.pop('q')
                    request.GET._mutable = False
                    qs = qs.filter(id=node.id)
                    break
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
            is_debug = field.choices.pop(0)[0] == Node.DEBUG
            assert is_debug, "Problem removing DEBUG from set_state"
        return field
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Warning user if the node is not fully configured """
        if request.method == 'GET':
            obj = self.get_object(request, object_id)
            if obj and not obj.cert:
                messages.warning(request, 'This node lacks a valid certificate.')
            if obj and not obj.group.allow_nodes:
                msg = "The node group does not have permissions to manage nodes"
                messages.warning(request, msg)
            # Show node name in page title (#362)
            if obj:
                extra_context = extra_context or {}
                extra_context.update({'title': 'Change node "%s"' % obj.name})
        return super(NodeAdmin, self).change_view(request, object_id,
                form_url=form_url, extra_context=extra_context)


class ServerPropInline(PermissionTabularInline):
    model = ServerProp
    extra = 1
    verbose_name_plural = mark_safe('Server properties %s' % docstring_as_help_tip(ServerProp))
    
    class Media:
        js = ('nodes/js/collapsed_node_properties.js',)


class ServerAdmin(ChangeViewActions, SingletonModelAdmin, PermissionModelAdmin):
    change_form_template = 'admin/nodes/server/change_form.html'
    inlines = [ServerPropInline]
    
    def has_delete_permission(self, *args, **kwargs):
        """ It doesn't make sense to delete the server """
        return False


class IslandAdmin(PermissionModelAdmin):
    list_display = ['name', 'id', 'description']
    search_fields = ['name', 'description']


admin.site.register(Node, NodeAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Island, IslandAdmin)

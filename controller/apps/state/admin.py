from __future__ import absolute_import

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from controller.admin import ChangeViewActions
from controller.admin.utils import (insert_list_display, get_admin_link, colored,
    insert_list_filter, insert_action, get_modeladmin)
from nodes.models import Node
from permissions.admin import PermissionModelAdmin
from slices.admin import SliverInline, NodeListAdmin, SliceSliversAdmin
from slices.models import Sliver

from .actions import refresh, refresh_state, state_action
from .models import NodeState, SliverState
from .settings import STATE_NODE_SOFT_VERSION_URL


STATES_COLORS = {
    'offline': 'red',
    'debug': 'darkorange',
    'safe': 'grey',
    'production': 'green',
    'failure': 'red',
    'online': 'green',
    'unknown': 'grey',
    'registered': 'grey',
    'deployed': 'darkorange',
    'started': 'green',
    'fail_alloc': 'red',
    'fail_deploy': 'red',
    'fail_start': 'red' }


class BaseStateAdmin(ChangeViewActions, PermissionModelAdmin):
    readonly_fields = ['node_link', 'last_seen_on', 'last_try_on', 'next_retry_on',
        'current', 'display_metadata', 'display_data']
    fieldsets = (
        (None, {
            'fields': ('node_link', 'last_seen_on', 'last_try_on', 'next_retry_on',
                       'current',)
        }),
        ('Details', {
            'fields': ('display_metadata', 'display_data')
        }),)
    change_view_actions = [refresh]
    change_form_template = "admin/controller/change_form.html"
    
    class Media:
        css = { "all": ("controller/css/github.css", "state/admin/css/details.css") }
    
    def node_link(self, instance):
        """ Link to related node used on change_view """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.get_node()))
    node_link.short_description = 'Node'
    
    def display_data(self, instance):
        style = '<style>code,pre {font-size:1.13em;}</style><br></br>'
        # TODO render data according to header content-type
        #      (when it becomes available in the node)
        return mark_safe(style + highlight(instance.data, JsonLexer(), HtmlFormatter()))
    display_data.short_description = 'data'
    
    def display_metadata(self, instance):
        style = '<style>code,pre {font-size:1.13em;}</style><br></br>'
        return mark_safe(style + highlight(instance.metadata, JsonLexer(), HtmlFormatter()))
    display_metadata.short_description = 'metadata'
    
    def current(self, instance):
        return mark_safe(colored('current', STATES_COLORS, verbose=True)(instance))
    
    def has_delete_permission(self, *args, **kwargs):
        return False


class NodeStateAdmin(BaseStateAdmin):
    readonly_fields = ['last_contact_on'] + BaseStateAdmin.readonly_fields
    fieldsets = (
        (None, {
            'fields': ('node_link', 'last_seen_on', 'last_contact_on',
                       'last_try_on', 'next_retry_on', 'current',)
        }),
        ('Details', {
            'fields': ('display_metadata', 'display_data')
        }),)
    change_form_template = 'admin/state/nodestate/change_form.html'


class SliverStateAdmin(BaseStateAdmin):
    readonly_fields = ['sliver_link'] + BaseStateAdmin.readonly_fields
    fieldsets = (
        (None, {
            'fields': ('sliver_link', 'node_link', 'last_seen_on', 'last_try_on',
                       'next_retry_on', 'current',)
        }),
        ('Details', {
            'fields': ('display_metadata', 'display_data')
        }),)
    change_form_template = 'admin/state/sliverstate/change_form.html'
    
    def sliver_link(self, instance):
        """ Link to related sliver used on change_view """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.sliver))
    sliver_link.short_description = 'Sliver'


admin.site.register(NodeState, NodeStateAdmin)
admin.site.register(SliverState, SliverStateAdmin)


# Monkey Patch section

def state_link(*args):
    obj = args[-1]
    color = colored('current', STATES_COLORS, verbose=True)
    try:
        state = obj.state
    except (NodeState.DoesNotExist, SliverState.DoesNotExist):
        return 'No data'
    else:
        model_name = obj._meta.verbose_name_raw
        url = reverse('admin:state_%sstate_change' % model_name, args=[state.pk])
        return mark_safe('<a href="%s">%s</a>' % (url, color(state)))
state_link.admin_order_field = 'state__last_seen_on'


def soft_version(node):
    try:
        version = node.state.soft_version
    except NodeState.DoesNotExist:
        return 'No data'
    else:
        if not version:
            return 'No data'
        url = STATE_NODE_SOFT_VERSION_URL(version)
        return mark_safe('<a href="%s">%s</a>' % (url, version))
soft_version.admin_order_field = 'state__soft_version'


insert_list_display(Node, soft_version)
insert_list_display(NodeListAdmin, soft_version)
insert_list_display(Node, state_link)
insert_list_display(NodeListAdmin, state_link)
insert_list_display(Sliver, state_link)
insert_action(Node, refresh_state)
insert_action(Sliver, refresh_state)
insert_list_filter(Node, 'state__soft_version')
SliverInline.sliver_state = state_link
SliverInline.readonly_fields.append('sliver_state')
SliverInline.fields.append('sliver_state')

node_modeladmin = get_modeladmin(Node)
node_modeladmin.set_change_view_action(state_action)
sliver_modeladmin = get_modeladmin(Sliver)
sliver_modeladmin.set_change_view_action(state_action)
# TODO
#actions = getattr(SliceSliversAdmin, 'change_view_actions', [])
#SliceSliversAdmin.change_view_actions = actions + [state_action]

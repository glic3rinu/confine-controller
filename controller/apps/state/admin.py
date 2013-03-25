from __future__ import absolute_import

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from controller.admin.utils import insert_list_display, get_admin_link, colored
from nodes.models import Node
from permissions.admin import PermissionModelAdmin
from slices.admin import SliverInline
from slices.models import Sliver

from .models import NodeState, SliverState


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


class BaseStateAdmin(PermissionModelAdmin):
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
    
    class Media:
        css = { "all": ("controller/css/github.css",) }
    
    def node_link(self, instance):
        """ Link to related node used on change_view """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.get_node()))
    node_link.short_description = 'Node'
    
    def display_data(self, instance):
        style = '<style>code,pre {font-size:1.13em;}</style><br></br>'
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
        return mark_safe("<b>%s</b>" % get_admin_link(instance))
    sliver_link.short_description = 'Sliver'


admin.site.register(NodeState, NodeStateAdmin)
admin.site.register(SliverState, SliverStateAdmin)

# Monkey Patch section

def state(*args):
    obj = args[-1]
    color = colored('current', STATES_COLORS, verbose=True)
    try:
        state = obj.state
    except (NodeState.DoesNotExist, SliverState.DoesNotExist):
        return 'No data'
    else:
        cls_name = type(state).__name__.lower()
        url = reverse('admin:state_%s_change' % cls_name, args=[state.pk])
        return mark_safe('<a href="%s">%s</a>' % (url, color(state)))
state.admin_order_field = 'state__last_seen_on'


insert_list_display(Node, state)
insert_list_display(Sliver, state)
SliverInline.sliver_state = state
SliverInline.readonly_fields.append('sliver_state')
SliverInline.fields.append('sliver_state')


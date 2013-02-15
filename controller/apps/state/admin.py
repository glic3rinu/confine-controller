from __future__ import absolute_import

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from controller.admin.utils import insert_list_display, get_admin_link
from nodes.models import Node
from permissions.admin import PermissionModelAdmin

from .models import NodeState


STATES_COLORS = {
    NodeState.OFFLINE: 'red',
    NodeState.ONLINE: 'green', }


class NodeStateAdmin(PermissionModelAdmin):
    readonly_fields = ['node_link', 'last_success_on', 'last_retry_on', 'current', 'metadata']
    fieldsets = (
        (None, {
            'fields': ('node_link', 'last_success_on', 'last_retry_on', 'current')
        }),
        ('Details', {
            'classes': ('collapse',),
            'fields': ('metadata',)
        }),)
    change_form_template = 'admin/state/nodestate/change_form.html'
    
    def node_link(self, instance):
        """ Link to related node used on change_view """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.node))
    node_link.short_description = 'Node'


admin.site.register(NodeState, NodeStateAdmin)


# Monkey Patch section

def state(node):
    try:
        state = node.state
    except NodeState.DoesNotExist:
        state = NodeState.OFFLINE
        color = STATES_COLORS.get(state, 'black')
        return mark_safe('<b><span style="color: %s;">%s</span></b>' % (color, state))
    else:
        color = STATES_COLORS.get(state.current, "black")
        url = reverse('admin:state_nodestate_change', args=[state.pk])
        return mark_safe('<a href="%s"><b><span style="color: %s;">%s</span></b></a>' % (url, color, state.current))
state.admin_order_field = 'state__last_success_on'

insert_list_display(Node, state)

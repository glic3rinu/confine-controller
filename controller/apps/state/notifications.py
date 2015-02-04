from __future__ import absolute_import

from datetime import timedelta
from django.db.models import Q
from django.utils import timezone

from nodes.models import Node
from notifications import Notification
from users.models import Group, Roles

from .models import State
from .settings import STATE_NODE_OFFLINE_WARNING, STATE_NODE_SAFE_WARNING


class NodeNotAvailable(Notification):
    """ Notify when a node goes offline and remains unavailable """
    model = Group # we want to aggregate nodes by group
    description = 'Notificate %s days after the node goes offline' % STATE_NODE_OFFLINE_WARNING.days
    verbose_name = 'Node not available notification'
    default_subject = 'Group {{ group.name }} has {{ nodes|length }} node(s) OFFLINE for more than {{ exp_warn.days }} days'
    default_message = (
        'Dear node administrator\n\n'
        'This is a report about your group nodes that appear as offline.\n'
        'Please visit the following URLs to check their configuration:\n'
        '{% for node in nodes %}\n'
        '    {% ifchanged node.set_state %} == set_state {{ node.set_state|upper }} == {% endifchanged %}\n'
        '    - {{ node }} http://{{ site.domain }}{% url \'admin:nodes_node_change\' node.pk %}\n'
        '{% endfor %}')
    expire_window = timedelta(days=7)
    
    def _node_unavailable(self, node):
        """Check that node is offline or nodata for a defined time."""
        unavailable_states = [State.OFFLINE, State.NODATA]
        state = node.state
        if state.current not in unavailable_states:
            return False
        
        # check if the node has been unavailable allways since
        # STATE_NODE_OFFLINE_WARNING ago (by default 5 days)
        end_time = timezone.now()
        start_time = end_time - STATE_NODE_OFFLINE_WARNING
        history = state.history.filter(Q(start__range=(start_time, end_time)) |
                                       Q(end__range=(start_time, end_time)))
        available_history = history.exclude(value__in=unavailable_states)
        return history.count() > 0 and not available_history.exists()
        
    def check_condition(self, obj):
        for node in obj.nodes.all():
            if self._node_unavailable(node):
                return True
        return False
    
    def get_recipients(self, obj):
        return obj.get_emails(roles=[Roles.NODE_ADMIN])
    
    def get_context(self, obj):
        context = super(NodeNotAvailable, self).get_context(obj)
        nodes_unavailable = []
        for node in obj.nodes.all().order_by('set_state'):
            if self._node_unavailable(node):
                nodes_unavailable.append(node)
        context.update({
            'group': obj,
            'nodes': nodes_unavailable,
            'exp_warn': STATE_NODE_OFFLINE_WARNING
        })
        return context


class NodeSafeState(Notification):
    """
    Notify when a node has set state to SAFE for maintenance
    but the node admin probably has forgot to set to PRODUCTION
    after a few days.
    """
    model = Node
    description = 'Notificate that the node is in %s state' % Node.SAFE
    verbose_name = 'Node in safe set_state notification'
    default_subject = ('Node {{ node.name }} in %s set_state for more than '
        '{{ exp_warn.days}} days' % Node.SAFE)
    default_message = (
        'Dear node administrator\n'
        'A few time ago you have set to SAFE your node, that probably means that '
        'is under maintenance. Please, remember setting again to PRODUCTION because '
        'otherwise it cannot be usable in the testbed.\n'
        'To check the configuration of this node, please visit\n'
        'http://{{ site.domain }}{% url \'admin:nodes_node_change\' node.pk %}.\n'
        'Thanks!')
    
    def check_condition(self, obj):
        offline = obj.set_state == Node.SAFE
        last_production = obj.state.history.filter(value=Node.PRODUCTION).first()
        threshold = last_production and last_production.end < timezone.now() - STATE_NODE_SAFE_WARNING
        return offline and threshold

    def get_recipients(self, obj):
        return obj.group.get_emails(roles=[Roles.NODE_ADMIN])
    
    def get_context(self, obj):
        context = super(NodeSafeState, self).get_context(obj)
        context.update({
            'node': obj,
            'exp_warn': STATE_NODE_SAFE_WARNING
        })
        return context

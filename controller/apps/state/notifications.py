from __future__ import absolute_import

from django.utils import timezone

from nodes.models import Node
from notifications import Notification
from users.models import Roles

from .models import State
from .settings import STATE_NODE_OFFLINE_WARNING, STATE_NODE_SAFE_WARNING


class NodeNotAvailable(Notification):
    """ Notify when a node goes offline and remains unavailable """
    model = Node
    description = 'Notificate %s days after the node goes offline' % STATE_NODE_OFFLINE_WARNING.days
    verbose_name = 'Node not available notification'
    default_subject = 'Node {{ node.name }} appear OFFLINE for more than {{ exp_warn.days }} days'
    default_message = (
        'Dear node operator\n'
        'Your node appear as offline.\n'
        'To check the configuration of this node, please visit\n'
        'http://{{ site.domain }}{% url \'admin:nodes_node_change\' node.pk %}.')
    
    def check_condition(self, obj):
        state = obj.state
        offline = state.current == State.OFFLINE
        threshold = state.last_change_on < timezone.now() - STATE_NODE_OFFLINE_WARNING
        return offline and threshold
    
    def get_recipients(self, obj):
        return obj.group.get_emails(roles=[Roles.GROUP_ADMIN, Roles.NODE_ADMIN])
    
    def get_context(self, obj):
        context = super(NodeNotAvailable, self).get_context(obj)
        context.update({
            'node': obj,
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
        return obj.group.get_emails(roles=[Roles.GROUP_ADMIN, Roles.NODE_ADMIN])
    
    def get_context(self, obj):
        context = super(NodeNotAvailable, self).get_context(obj)
        context.update({
            'node': obj,
            'exp_warn': STATE_NODE_SAFE_WARNING
        })
        return context

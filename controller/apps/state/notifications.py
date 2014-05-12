from __future__ import absolute_import

from django.utils import timezone

from nodes.models import Node
from notifications import Notification
from users.models import Roles

from .models import State
from .settings import STATE_NODE_OFFLINE_WARNING


class NodeNotAvailable(Notification):
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

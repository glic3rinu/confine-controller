from __future__ import absolute_import

from django.utils import timezone

from notifications import Notification

from .models import State
from .settings import STATE_NODE_OFFLINE_WARNING


class NodeNotAvailable(Notification):
    model = State
    description = 'Notificate %s days after the node goes offline' % STATE_NODE_OFFLINE_WARNING.days
    verbose_name = 'Node not available notification'
    default_subject = 'Node {{ node.name }} appear OFFLINE for more than {{ exp_warn.days }} days'
    default_message = (
        'Dear node operator\n'
        'Your node appear as offline')
    
    def check_condition(self, obj):
        offline = obj.current == State.OFFLINE
        threshold = obj.last_change_on < timezone.now()-STATE_NODE_OFFLINE_WARNING
        return offline and threshold
    
    def get_recipients(self, obj):
        return obj.node.group.get_emails(role='admin')
    
    def get_context(self, obj):
        context = super(NodeNotAvailable, self).get_context(obj)
        context.update({
            'slice': obj,
            'exp_warn': STATE_NODE_OFFLINE_WARNING
        })
        return context

from __future__ import absolute_import

from django.utils import timezone

from notifications import Notification

from .models import NodeState


email_days = 10

class NodeNotAvailable(Notification):
    model = NodeState
    description = 'Notificate %s days before the slice expires' % email_days
    verbose_name = 'Node not available notification'
    
    def check_condition(self, obj):
        return (obj.current == obj.OFFLINE and obj.last_change_on < timezone.now()-email_days)
    
    def get_recipients(self, ob):
        return obj.node.group.admins.list_values('email')

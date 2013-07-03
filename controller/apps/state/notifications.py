from __future__ import absolute_import

from django.utils import timezone

from notifications import Notification

from .models import NodeState


email_days = 10

class NodeNotAvailable(Notification):
    model = NodeState
    description = 'Notificate %s days after the node goes offline' % email_days
    verbose_name = 'Node not available notification'
    default_subject = ''
    default_message = ''
    
    def check_condition(self, obj):
        return (obj.current == obj.OFFLINE and obj.last_change_on < timezone.now()-email_days)
    
    def get_recipients(self, ob):
        return obj.node.group.admins.list_values('email')
    
    def get_context(self, obj):
         return {
            'obj': obj,
            'notification_time': SLICES_SLICE_EXP_WARN,}

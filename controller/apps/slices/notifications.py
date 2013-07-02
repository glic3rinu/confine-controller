from __future__ import absolute_import

from django.utils import timezone

from notifications import Notification

from .models import Slice


email_days = 10

class SliceExpiration(Notification):
    model = Slice
    description = 'Notificate %s days before the slice expires' % email_days
    verbose_name = 'Slice expiration notification'
    
    def check_condition(self, obj):
        return obj.expires_on > timezone.now()+email_days
    
    def get_recipients(self, obj):
        return obj.group.admins.list_values('email')

from __future__ import absolute_import

from django.utils import timezone

from notifications import Notification

from .models import Slice
from .settings import SLICES_SLICE_EXP_WARN


class SliceExpiration(Notification):
    model = Slice
    description = 'Notificate %s days before the slice expires' % SLICES_SLICE_EXP_WARN
    verbose_name = 'Slice expiration notification'
    default_subject = 'Slice {{ slice.name }} expires in {{ notification_time.days }} days'
    default_message = (
        'Hi,\n'
        'Your slice "{{ slice.name }}" will expire in {{ notification_time.days }} days.\n'
        'To update, renew, or delete this slice, please visit\n'
        'http://{{ site.domain }}{% url \'admin:slices_slice_change\' slice.pk %}\n'
        '\n'
        'Thanks,\n'
        'Ops team.\n')
    
    def check_condition(self, obj):
        return obj.expires_on > timezone.now()+SLICES_SLICE_EXP_WARN
    
    def get_recipients(self, obj):
        return obj.group.get_admin_emails()
    
    def get_context(self, obj):
        context = super(SliceExpiration, self).get_context(obj)
        context.update({
            'slice': obj,
            'notification_time': SLICES_SLICE_EXP_WARN,})
        return context


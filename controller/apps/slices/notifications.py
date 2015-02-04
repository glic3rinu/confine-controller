from __future__ import absolute_import

from django.utils import timezone

from notifications import Notification
from users.models import Roles

from .models import Slice
from .settings import SLICES_SLICE_EXP_WARN


class SliceExpiration(Notification):
    model = Slice
    description = 'Notificate %s days before the slice expires' % SLICES_SLICE_EXP_WARN.days
    verbose_name = 'Slice expiration notification'
    default_subject = 'Slice {{ slice.name }} expires in {{ expiration_days }} days'
    default_message = (
        'Hi,\n'
        'Your slice "{{ slice.name }}" will expire in {{ expiration_days }} days.\n'
        'To update, renew, or delete this slice, please visit\n'
        'http://{{ site.domain }}{% url \'admin:slices_slice_change\' slice.pk %}\n'
        '\n'
        'Thanks,\n'
        'Ops team.\n')
    
    def check_condition(self, obj):
        threshold = (timezone.now()+SLICES_SLICE_EXP_WARN).date()
        return obj.expires_on <= threshold
    
    def get_recipients(self, obj):
        return obj.group.get_emails(roles=[Roles.SLICE_ADMIN])
    
    def get_context(self, obj):
        context = super(SliceExpiration, self).get_context(obj)
        context.update({
            'slice': obj,
            'expiration_days': (obj.expires_on-timezone.now().date()).days
        })
        return context



from datetime import datetime, timedelta
import textwrap

from celery.task import task, periodic_task
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.conf import settings as project_settings
from django.db import transaction

from .settings import CLEAN_EXPIRED_SLICES_CRONTAB, SLICE_EXPIRATION_WARNING


@periodic_task(name="slices.clean_expired_slices", run_every=CLEAN_EXPIRED_SLICES_CRONTAB)
def clean_expired_slices():
    """ 
    Delete expired slices and warn admins about slices that are about to expire
    """
    from slices.models import Slice
    now = datetime.now()
    
    # Delete expired slices
    deletable_slices = Slice.objects.filter(expires_on__lte=now)
    for slice in deletable_slices:
        with transaction.commit_on_success():
            slice.delete()
    
    # warn about slices that are about to expire
    warning_slices = Slice.objects.filter(expires_on__lte=now+SLICE_EXPIRATION_WARNING,
                                          expires_on__gt=now+SLICE_EXPIRATION_WARNING-timedelta(1))
    for slice in warning_slices:
        # TODO allow message customization
        subject = '[Confine] slice %s expires in %s days' % (slice.name, SLICE_EXPIRATION_WARNING.days)
        renew_url = 'https://controller.confine-project.eu%s' % reverse('admin:slices_slice_change', args=[slice.pk])
        message = textwrap.dedent("""\
            Your slice "%s" will expire in %s days.
            
            To update, renew, or delete this slice, please visit the URL: 
            
                %s
            
            Thanks,
            Confine ops.""" % (slice.name, SLICE_EXPIRATION_WARNING.days, renew_url))
        from_address = project_settings.MAINTAINANCE_FROM_EMAIL
        to = slice.group.get_admin_emails()
        send_mail(subject, message, from_address, to, fail_silently=False)
    
    # Just for the record
    format = lambda slice: '<%s "%s">' % (slice.id, slice.name)
    return ', '.join(map(format, deletable_slices))


@task(name="slices.force_slice_update")
def force_slice_update(slice_id):
    from slices.models import Slice
    slice = Slice.objects.get(pk=slice_id)
    for sliver in slice.slivers_set.all():
        force_sliver_update(seliver.pk)


@task(name="slices.force_sliver_update")
def force_sliver_update(sliver_id):
    from slices.models import Sliver
    sliver = Sliver.objects.get(pk=sliver_id)
    return "NOT IMPLEMENTED"

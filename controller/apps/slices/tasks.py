from datetime import datetime, timedelta
import textwrap

from celery.task import task, periodic_task
from celery.task.schedules import crontab
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.conf import settings as project_settings
from django.db import transaction

from controller.utils import send_email_template

from .settings import SLICES_SLICE_EXP_WARN_DAYS


@periodic_task(name="slices.clean_expired_slices", run_every=crontab(minute=0, hour=0))
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
    email_days = timedelta(SLICES_SLICE_EXP_WARN_DAYS)
    warning_slices = Slice.objects.filter(expires_on__gte=now+email_days,
                                          expires_on__lte=now+email_days+timedelta(1))
    for slice in warning_slices:
        context = {'slice': slice,
                   'days': SLICES_SLICE_EXP_WARN_DAYS,}
        template = 'slices/slice_expiration_warning.email'
        to = slice.group.get_admin_emails()
        send_email_template(context=context, template=template, to=to)
    
    # Just for the record
    format = lambda slice: '<%s "%s">' % (slice.id, slice.name)
    return ', '.join(map(format, deletable_slices))


@task(name="slices.force_slice_update")
def force_slice_update(slice_id):
    from slices.models import Slice
    slice = Slice.objects.get(pk=slice_id)
    for sliver in slice.slivers.all():
        force_sliver_update(seliver.pk)


@task(name="slices.force_sliver_update")
def force_sliver_update(sliver_id):
    from slices.models import Sliver
    sliver = Sliver.objects.get(pk=sliver_id)
    return "NOT IMPLEMENTED"

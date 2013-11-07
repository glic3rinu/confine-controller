from celery.task import task, periodic_task
from celery.task.schedules import crontab
from django.db import transaction
from django.utils import timezone


@periodic_task(name="slices.clean_expired_slices", run_every=crontab(minute=0, hour=0))
def clean_expired_slices():
    """ Delete expired slices """
    from slices.models import Slice
    now = timezone.now()
    
    # Delete expired slices
    deletable_slices = Slice.objects.filter(expires_on__lte=now)
    for slice in deletable_slices:
        with transaction.atomic():
            slice.delete()
    
    # Just for the record
    format = lambda slice: '<%s "%s">' % (slice.id, slice.name)
    return ', '.join(map(format, deletable_slices))


@task(name="slices.force_slice_update")
def force_slice_update(slice_id):
    from slices.models import Slice
    slice = Slice.objects.get(pk=slice_id)
    for sliver in slice.slivers.all():
        force_sliver_update(sliver.pk)


@task(name="slices.force_sliver_update")
def force_sliver_update(sliver_id):
    from slices.models import Sliver
    sliver = Sliver.objects.get(pk=sliver_id)
    return "NOT IMPLEMENTED"

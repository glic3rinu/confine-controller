from celery.task import task, periodic_task
from datetime import datetime
from django.db import transaction
from slices.settings import CLEAN_EXPIRED_SLICES_CRONTAB


@periodic_task(name="Clean Expired Slices", run_every=CLEAN_EXPIRED_SLICES_CRONTAB)
def clean_expired_slices():
    from slices.models import Slice
    now = datetime.now()
    deletable_slices = Slice.objects.filter(expires_on__lte=now)
    for slice in deletable_slices:
        with transaction.commit_on_success():
            slice.delete()
    format = lambda slice: '<%s "%s">' % (slice.id, slice.name)
    return ', '.join(map(format, deletable_slices))


@task(name="Force Slice Update")
def force_slice_update(slice_id):
    from slices.models import Slice
    slice = Slice.objects.get(pk=slice_id)
    for sliver in slice.slivers_set.all():
        force_sliver_update(seliver.pk)


@task(name="Force Sliver Update")
def force_sliver_update(sliver_id):
    from slices.models import Sliver
    sliver = Sliver.objects.get(pk=sliver_id)
    return "NOT IMPLEMENTED"

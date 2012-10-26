from celery.task import periodic_task
from datetime import datetime
from django.db import transaction
from slices.models import Slice
from slices.settings import CLEAN_EXPIRED_SLICES_CRONTAB


@periodic_task(name="Clean Expired Slices", run_every=CLEAN_EXPIRED_SLICES_CRONTAB)
def clean_expired_slices():
    now = datetime.now()
    deletable_slices = Slice.objects.filter(exp_date__lte=now)
    for slice in deletable_slices:
        with transaction.commit_on_success():
            slice.delete()
    format = lambda slice: '<%s "%s">' % (slice.id, slice.name)
    return ', '.join(map(format, deletable_slices))


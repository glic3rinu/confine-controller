from celery.task import periodic_task
from celery.task.schedules import crontab
from django.db import transaction

from .models import Notification


@periodic_task(name="notifications.notify", run_every=crontab(minute=0, hour=0))
def notify(ids=[]):
    if ids:
        notifications = Notification.objects.filter(pk__in=ids)
    else:
        notifications = Notification.objects.active()
    for notification in notifications:
        with transaction.atomic():
            notification.process()

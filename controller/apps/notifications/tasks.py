from celery.task import periodic_task
from celery.task.schedules import crontab
from django.db import transaction


@periodic_task(name="notifications.notify", run_every=crontab(minute=0, hour=0))
def notify():
    for notification in Notification.objects.active():
        with transaction.commit_on_success():
            notification.process()

from __future__ import absolute_import

from celery.task import periodic_task
from celery.task.schedules import crontab

@periodic_task(name="users.clean_expired_users", run_every=crontab(minute=0, hour=0))
def clean_expired_users():
    """
    Delete expired registered users.
    """
    from registration.models import RegistrationProfile
    
    RegistrationProfile.objects.delete_expired_users()
    

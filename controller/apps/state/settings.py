from celery.task.schedules import crontab
from django.conf import settings

ugettext = lambda s: s


STATE_LOCK_DIR = getattr(settings, 'STATE_LOCK_DIR', '/dev/shm/')


STATE_NODESTATE_URI = getattr(settings, 'STATE_NODESTATE_URI',
    'http://[%(mgmt_addr)s]/confine/api/node/')

STATE_NODESTATE_CRONTAB = getattr(settings, 'STATE_NODESTATE_CRONTAB',
    crontab(minute='*/5', hour='*'))

STATE_NODESTATE_FREQUENCY = getattr(settings, 'STATE_NODESTATE_FREQUENCY', 300)

STATE_NODESTATE_EXPIRE_WINDOW = getattr(settings, 'STATE_NODESTATE_EXPIRE_WINDOW', 450)


STATE_SLIVERSTATE_URI = getattr(settings, 'STATE_SLIVERSTATE_URI',
    'http://[%(mgmt_addr)s]/confine/api/slivers/%(object_id)d')

STATE_SLIVERSTATE_CRONTAB = getattr(settings, 'STATE_SLIVERSTATE_CRONTAB',
    crontab(minute='*/5', hour='*'))

STATE_SLIVERSTATE_FREQUENCY = getattr(settings, 'STATE_SLIVERSTATE_FREQUENCY', 300)

STATE_SLIVERSTATE_EXPIRE_WINDOW = getattr(settings, 'STATE_SLIVERSTATE_EXPIRE_WINDOW', 450)

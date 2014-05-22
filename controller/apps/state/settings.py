from datetime import timedelta

from django.conf import settings


STATE_LOCK_DIR = getattr(settings, 'STATE_LOCK_DIR', '/dev/shm/')

STATE_NODE_PULL_TIMEOUT = getattr(settings, 'STATE_NODE_PULL_TIMEOUT', timedelta(hours=2))


STATE_NODE_URI = getattr(settings, 'STATE_NODESTATE_URI',
    'http://[%(mgmt_addr)s]/confine/api/node/')

STATE_SCHEDULE = getattr(settings, 'STATE_SCHEDULE', 200)

# Percentage
STATE_EXPIRE_WINDOW = getattr(settings, 'STATE_EXPIRE_WINDOW', 350)

STATE_FLAPPING_CHANGES = getattr(settings, 'STATE_FLAPPING_CHANGES', 2)

STATE_FLAPPING_MINUTES = getattr(settings, 'STATE_FLAPPING_MINUTES', 15)

STATE_SLIVER_URI = getattr(settings, 'STATE_SLIVER_URI',
    'http://[%(mgmt_addr)s]/confine/api/slivers/%(object_id)d/')


STATE_NODE_SOFT_VERSION_URL = getattr(settings, 'STATE_NODE_SOFT_VERSION_URL',
    lambda version: ('http://redmine.confine-project.eu/projects/confine/repository/'
                     'show?branch=%s&rev=%s' % tuple(version.split('-')[0].split('.'))))


STATE_NODE_SOFT_VERSION_NAME = getattr(settings, 'STATE_NODE_SOFT_VERSION_NAME',
    lambda version: '%s.%s' % (version.split('.')[0], version.split('-')[1].split('.')[0]) if len(version.split('-')) > 1 else version)


STATE_NODE_OFFLINE_WARNING = getattr(settings, 'STATE_NODE_OFFLINE_WARNING', timedelta(days=1))

STATE_NODE_SAFE_WARNING = getattr(settings, 'STATE_NODE_SAFE_WARNING', timedelta(days=3))

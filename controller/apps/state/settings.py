from datetime import timedelta

from django.conf import settings


STATE_LOCK_DIR = getattr(settings, 'STATE_LOCK_DIR', '/dev/shm/')

STATE_NODE_PULL_TIMEOUT = getattr(settings, 'STATE_NODE_PULL_TIMEOUT', timedelta(hours=2))


STATE_NODESTATE_URI = getattr(settings, 'STATE_NODESTATE_URI',
    'http://[%(mgmt_addr)s]/confine/api/node/')

STATE_NODESTATE_SCHEDULE = getattr(settings, 'STATE_NODESTATE_SCHEDULE', 200)

# Percentage
STATE_NODESTATE_EXPIRE_WINDOW = getattr(settings, 'STATE_NODESTATE_EXPIRE_WINDOW', 150)


STATE_SLIVERSTATE_URI = getattr(settings, 'STATE_SLIVERSTATE_URI',
    'http://[%(mgmt_addr)s]/confine/api/slivers/%(object_id)d')

STATE_SLIVERSTATE_SCHEDULE = getattr(settings, 'STATE_SLIVERSTATE_SCHEDULE', 200)

# Percentage
STATE_SLIVERSTATE_EXPIRE_WINDOW = getattr(settings, 'STATE_SLIVERSTATE_EXPIRE_WINDOW', 150)


STATE_NODE_SOFT_VERSION_URL = getattr(settings, 'STATE_NODE_SOFT_VERSION_URL',
    lambda version: ('http://redmine.confine-project.eu/projects/confine/repository/'
                     'show?branch=%s&rev=%s' % tuple(version.split('-')[0].split('.'))))


STATE_NODE_SOFT_VERSION_NAME = getattr(settings, 'STATE_NODE_SOFT_VERSION_NAME',
    lambda version: '%s.%s' % (version.split('.')[0], version.split('-')[1]) if len(version.split('-')) > 1 else version)


STATE_NODE_OFFLINE_WARNING = getattr(settings, 'STATE_NODE_OFFLINE_WARNING', timedelta(days=1))

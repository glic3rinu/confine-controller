from datetime import timedelta

from django.conf import settings


STATE_LOCK_DIR = getattr(settings, 'STATE_LOCK_DIR', '/dev/shm/')

STATE_NODE_PULL_TIMEOUT = getattr(settings, 'STATE_NODE_PULL_TIMEOUT', timedelta(hours=2))

STATE_NODE_URI = getattr(settings, 'STATE_NODESTATE_URI',
    '%(base_uri)snode/')

STATE_SCHEDULE = getattr(settings, 'STATE_SCHEDULE', 200)

# node API request connect timeout
STATE_FETCH_TIMEOUT_CONNECT = getattr(settings, 'STATE_FETCH_TIMEOUT_CONNECT', 30)

# node API request read timeout
STATE_FETCH_TIMEOUT_READ = getattr(settings, 'STATE_FETCH_TIMEOUT_READ', 20)

# Percentage
STATE_EXPIRE_WINDOW = getattr(settings, 'STATE_EXPIRE_WINDOW', 350)

STATE_FLAPPING_CHANGES = getattr(settings, 'STATE_FLAPPING_CHANGES', 2)

STATE_FLAPPING_MINUTES = getattr(settings, 'STATE_FLAPPING_MINUTES', 15)

STATE_SLIVER_URI = getattr(settings, 'STATE_SLIVER_URI',
    '%(base_uri)sslivers/%(object_id)d/')


STATE_NODE_SOFT_VERSION_URL = getattr(settings, 'STATE_NODE_SOFT_VERSION_URL',
    lambda version: ('http://redmine.confine-project.eu/projects/confine/repository/'
                     'show?branch=%(branch)s&rev=%(rev)s' % version))


STATE_NODE_SOFT_VERSION_NAME = getattr(settings, 'STATE_NODE_SOFT_VERSION_NAME',
    lambda version: '%(branch)s.%(rev)s' % version)


STATE_NODE_OFFLINE_WARNING = getattr(settings, 'STATE_NODE_OFFLINE_WARNING', timedelta(days=5))

STATE_NODE_SAFE_WARNING = getattr(settings, 'STATE_NODE_SAFE_WARNING', timedelta(days=3))

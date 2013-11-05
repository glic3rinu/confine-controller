from django.conf import settings


# TODO move to base_settings.py

# ConfineParams
DEBUG_IPV6_PREFIX = getattr(settings, 'DEBUG_IPV6_PREFIX', 'fd5f:eee5:a6ad::/48')
PRIV_IPV6_PREFIX = getattr(settings, 'PRIV_IPV6_PREFIX', 'aa5f:eee5:a6ad::/48')


# TestbedParams
PRIV_IPV4_PREFIX_DFLT = getattr(settings, 'PRIV_IPV4_PREFIX_DFLT', '192.168.157.0/24')
SLIVER_MAC_PREFIX_DFLT = getattr(settings, 'SLIVER_MAC_PREFIX_DFLT', '0x06ab')
MGMT_IPV6_PREFIX = getattr(settings, 'MGMT_IPV6_PREFIX', '2001:db8:cafe::/48')


# Disable CSRF on login form allowing integration with other services
# TODO can this be replaced for CSRF_COOKIE_DOMAIN ?
DISABLE_LOGIN_CSRF_FROM = getattr(settings, 'DISABLE_LOGIN_CSRF_FROM', [])

# Domain name used when it will not be possible to infere the domain from a request
# For example in periodic tasks
SITE_URL = getattr(settings, 'SITE_URL', 'http://localhost')
SITE_NAME = getattr(settings, 'SITE_NAME', 'confine')
SITE_VERBOSE_NAME = getattr(settings, 'SITE_VERBOSE_NAME',
    '%s Testbed Management' % SITE_NAME.capitalize())


# Storage settings
# Extensions supported for renaming when uploading existing filenames
DOUBLE_EXTENSIONS = ('tar.gz', 'img.gz')


# Service managemente
START_SERVICES = getattr(settings, 'START_SERVICES',
    ['postgresql', 'tinc', 'celeryevcam', 'celeryd', 'celerybeat', [('uwsgi', 'nginx'), 'apache2',]])

RESTART_SERVICES = getattr(settings, 'RESTART_SERVICES',
    ['celeryd', 'celerybeat', ['apache2', 'uwsgi']])

STOP_SERVICES = getattr(settings, 'STOP_SERVICES',
    [['apache2', ('uwsgi', 'nginx')], 'celerybeat', 'celeryd', 'celeryevcam', 'tinc', 'postgresql'])


# Periodically clean orphan files task
CLEAN_ORPHAN_FILES = getattr(settings, 'CLEAN_ORPHAN_FILES', False)

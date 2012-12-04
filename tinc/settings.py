from django.conf import settings

ugettext = lambda s: s

TINC_DEFAULT_PORT = getattr(settings, 'TINC_DEFAULT_PORT', '666')

TINC_HOSTS_PATH = getattr(settings, 'TINC_SYS_PATH', '/etc/tinc/confine/hosts')

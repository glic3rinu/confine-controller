from django.conf import settings

ugettext = lambda s: s

TINC_DEFAULT_PORT = getattr(settings, 'TINC_DEFAULT_PORT', '666')

TINC_NET_NAME = getattr(settings, 'TINC_NET_NAME', 'confine')

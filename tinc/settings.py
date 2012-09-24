from django.conf import settings

ugettext = lambda s: s

TINC_DEFAULT_PORT = getattr(settings, 'TINC_DEFAULT_PORT', '666')

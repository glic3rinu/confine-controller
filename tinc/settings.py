from django.conf import settings

ugettext = lambda s: s

TINC_DEFAULT_PORT = getattr(settings, 'TINC_DEFAULT_PORT', '666')

TINC_NET_NAME = getattr(settings, 'TINC_NET_NAME', 'confine')

MGMT_IPV6_PREFIX = getattr(settings, 'MGMT_IPV6_PREFIX', '2001:db8:cafe::/48')

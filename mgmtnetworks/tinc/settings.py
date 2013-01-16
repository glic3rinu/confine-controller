from django.conf import settings

ugettext = lambda s: s

TINC_PORT_DFLT = getattr(settings, 'TINC_PORT_DFLT', '666')

TINC_NET_NAME = getattr(settings, 'TINC_NET_NAME', 'confine')

TINC_MGMT_IPV6_PREFIX = getattr(settings, 'TINC_MGMT_IPV6_PREFIX', '2001:db8:cafe::/48')

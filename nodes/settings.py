from django.conf import settings

ugettext = lambda s: s


RESEARCH_DEVICE_ARCHS = getattr(settings, 'RESEARCH_DEVICE_ARCHS', (
    ('x86', 'x86'),
    ('x86_64', 'x86_64'),
    ('ar71xx', 'ar71xx'),
))

DEFAULT_RESEARCH_DEVICE_ARCH = getattr(settings, 'DEFAULT_RESEARCH_DEVICE_ARCH', 'x86_64')


#TODO should the following options go into controller.settings ?

# ConfineParams
DEBUG_IPV6_PREFIX = getattr(settings, 'DEBUG_IPV6_PREFIX', 'fd5f:eee5:a6ad::/48')
PRIV_IPV6_PREFIX = getattr(settings, 'PRIV_IPV6_PREFIX', 'fd5f:eee5:a6ad::/48')


# TestbedParams
MGMT_IPV6_PREFIX = getattr(settings, 'MGMT_IPV6_PREFIX', '2001:db8:cafe::/48')
PRIV_IPV4_PREFIX_DFLT = getattr(settings, 'PRIV_IPV4_PREFIX_DFLT', '192.168.157.0/24')
SLIVER_MAC_PREFIX_DFLT = getattr(settings, 'SLIVER_MAC_PREFIX_DFLT', '0x06ab')

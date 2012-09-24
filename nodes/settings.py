from django.conf import settings

ugettext = lambda s: s


RESEARCH_DEVICE_ARCHS = getattr(settings, 'RESEARCH_DEVICE_ARCHS', (
    ('x86', 'x86'),
    ('amd64', 'amd64'),
    ('ar71xx', 'ar71xx'),
))

DEFAULT_RESEARCH_DEVICE_ARCH = getattr(settings, 'DEFAULT_RESEARCH_DEVICE_ARCH', 'amd64')


# ConfineParams
DEBUG_IPV6_PREFIX = getattr(settings, 'DEBUG_IPV6_PREFIX', 'fd5f:eee5:a6ad::/48')
PRIV_IPV6_PREFIX = getattr(settings, 'PRIV_IPV6_PREFIX', 'fd5f:eee5:a6ad::/48')

# TestbedParams
MGMT_IPV6_PREFIX = getattr(settings, 'MGMT_IPV6_PREFIX', 'fd5f:eee5:a6ad::/48')
PRIV_IPV4_PREFIX_DFLT = getattr(settings, 'PRIV_IPV4_PREFIX_DFLT', 'fd5f:eee5:a6ad::/48')
SLIVER_MAC_PREFIX_DFLT = getattr(settings, 'SLIVER_MAC_PREFIX_DFLT', 'fd5f:eee5:a6ad::/48')

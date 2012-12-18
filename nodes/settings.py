from django.conf import settings

ugettext = lambda s: s


NODE_ARCHS = getattr(settings, 'NODE_ARCHS', (
    ('x86', 'x86'),
    ('x86_64', 'x86_64'),
    ('ar71xx', 'ar71xx'),
    ('i586', 'i586'),
))

DEFAULT_NODE_ARCH = getattr(settings, 'DEFAULT_NODE_ARCH', 'x86_64')

DEFAULT_NODE_LOCAL_IFACE = getattr(settings, 'DEFAULT_NODE_LOCAL_IFACE', 'eth0')

#TODO should the following options go into controller.settings ?

# ConfineParams
DEBUG_IPV6_PREFIX = getattr(settings, 'DEBUG_IPV6_PREFIX', 'fd5f:eee5:a6ad::/48')
PRIV_IPV6_PREFIX = getattr(settings, 'PRIV_IPV6_PREFIX', 'fd5f:eee5:a6ad::/48')


# TestbedParams
PRIV_IPV4_PREFIX_DFLT = getattr(settings, 'PRIV_IPV4_PREFIX_DFLT', '192.168.157.0/24')
SLIVER_MAC_PREFIX_DFLT = getattr(settings, 'SLIVER_MAC_PREFIX_DFLT', '0x06ab')


# Certificate
# Path where the certificate files are stored
CERT_PATH = getattr(settings, 'CERT_PATH', '/tmp/')

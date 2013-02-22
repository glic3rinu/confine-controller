from django.conf import settings

ugettext = lambda s: s


NODES_NODE_ARCHS = getattr(settings, 'NODES_NODE_ARCHS', (
    ('x86', 'x86'),
    ('x86_64', 'x86_64'),
    ('ar71xx', 'ar71xx'),
    ('i586', 'i586'),
    ('i686', 'i686'),
))

NODES_NODE_ARCH_DFLT = getattr(settings, 'NODES_NODE_ARCH_DFLT', 'x86_64')

NODES_NODE_LOCAL_IFACE_DFLT = getattr(settings, 'NODES_NODE_LOCAL_IFACE_DFLT', 'eth0')

#TODO should the following options go into controller.settings ?

# ConfineParams
NODES_DEBUG_IPV6_PREFIX = getattr(settings, 'NODES_DEBUG_IPV6_PREFIX', 'fd5f:eee5:a6ad::/48')
NODES_PRIV_IPV6_PREFIX = getattr(settings, 'NODES_PRIV_IPV6_PREFIX', 'aa5f:eee5:a6ad::/48')


# TestbedParams
NODES_PRIV_IPV4_PREFIX_DFLT = getattr(settings, 'NODES_PRIV_IPV4_PREFIX_DFLT', '192.168.157.0/24')
NODES_SLIVER_MAC_PREFIX_DFLT = getattr(settings, 'NODES_SLIVER_MAC_PREFIX_DFLT', '0x06ab')


# Certificate
# Path where the certificate files are stored
NODES_CERT_PRIVATE_KEY_PATH = getattr(settings, 'NODES_CERT_PRIVATE_KEY_PATH', 
    '/etc/apache2/ssl/generic.confine-project.eu/generic.confine-project.eu.key')
# expiration time for generated certificates (4years)
NODES_CERT_EXPIRATION = getattr(settings, 'NODES_CERT_EXPIRATION', 60*60*24*365*4)


# Management backend, needed for management network IP
NODES_MGMT_BACKEND = getattr(settings, 'NODES_MGMT_BACKEND', 'mgmtnetworks.tinc.backend')

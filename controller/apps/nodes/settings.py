from django.conf import settings


NODES_NODE_ARCHS = getattr(settings, 'NODES_NODE_ARCHS', (
    ('x86_64', 'x86_64'),
    ('i586', 'i586'),
    ('i686', 'i686'),
))

NODES_NODE_ARCH_DFLT = getattr(settings, 'NODES_NODE_ARCH_DFLT', 'x86_64')

NODES_NODE_LOCAL_IFACE_DFLT = getattr(settings, 'NODES_NODE_LOCAL_IFACE_DFLT', 'eth0')

NODES_NODE_SLIVER_PUB_IPV4_DFLT = getattr(settings, 'NODES_NODE_SLIVER_PUB_IPV4_DFLT', 'dhcp')

NODES_NODE_SLIVER_PUB_IPV4_RANGE_DFLT = getattr(settings, 'NODES_NODE_SLIVER_PUB_IPV4_RANGE_DFLT', '#8')

NODES_NODE_DIRECT_IFACES_DFLT = getattr(settings, 'NODES_NODE_DIRECT_IFACES_DFLT', [])


# expiration time for generated certificates (4years)
NODES_CERT_EXP_DAYS = getattr(settings, 'NODES_CERT_EXP_DAYS', 60*60*24*365*4)


# Management backend, needed for management network IP
NODES_MGMT_BACKEND = getattr(settings, 'NODES_MGMT_BACKEND', 'mgmtnetworks.tinc.backend')

NODES_NODE_API_NODE_BASE_URL = getattr(settings, 'NODES_NODE_API_NODE_BASE',
    'http://[%(mgmt_addr)s]/confine/api')

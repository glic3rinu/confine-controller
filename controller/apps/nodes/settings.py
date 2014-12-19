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

NODES_NODE_API_BASE_URI_DEFAULT = getattr(settings, 'NODES_NODE_API_BASE_URI_DEFAULT',
    'https://[%(mgmt_addr)s]/confine/api/')

NODES_SERVER_API_BASE_URI_DEFAULT = getattr(settings, 'NODES_SERVER_API_BASE_URI_DEFAULT',
    'https://[%(mgmt_addr)s]/api/')

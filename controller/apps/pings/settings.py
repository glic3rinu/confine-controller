from datetime import timedelta

from django.conf import settings


PING_LOCK_DIR = getattr(settings, 'PING_LOCK_DIR', '/dev/shm/')

PING_COUNT = getattr(settings, 'PING_COUNT', 4)

PING_INSTANCES = getattr(settings, 'PING_INSTANCES', (
    {
        'model': 'tinc.TincClient',
        'admin_classes': (
            ('TincClientInline', 'tinc_compatible_address', '', 'content_object'),
            ('HostAdmin', 'address', 'tinc', ''),),
        'app': 'mgmtnetworks.tinc',
        'schedule': 200,
        'expire_window': 150,
        'get_addr': lambda obj: getattr(obj, 'address') },
    {
        'model': 'slices.SliverIface',
        'admin_classes': (
            ('SliverIfaceInline', 'ipv6_addr', '', 'sliver'),),
        'app': 'slices',
        'schedule': 200,
        'expire_window': 150,
        'filter': {'type': 'management'},
        'get_addr': lambda obj: getattr(obj, 'ipv6_addr') }
    ))


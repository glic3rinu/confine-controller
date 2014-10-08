from dateutil.relativedelta import relativedelta
from datetime import timedelta

from django.conf import settings


PING_LOCK_DIR = getattr(settings, 'PING_LOCK_DIR', '/dev/shm/')


PING_COUNT = getattr(settings, 'PING_COUNT', 4)


PING_DEFAULT_INSTANCE = getattr(settings, 'PING_DEFAULT_INSTANCE', (
    {
        'schedule': 200,
        'expire_window': 150,
        'downsamples': (
            # Limitations: you can not say 16 months or 40 days
            #              but you can say 2 years or 2 months
            (relativedelta(years=1), timedelta(minutes=240)),
            (relativedelta(months=6), timedelta(minutes=60)),
            (relativedelta(months=3), timedelta(minutes=20)),
            (relativedelta(months=2), timedelta(minutes=10)),
            (relativedelta(weeks=2), timedelta(minutes=5)),
        ),
        'get_addr': lambda obj: getattr(obj, 'address')
    }
))


PING_INSTANCES = getattr(settings, 'PING_INSTANCES', (
    {
        'model': 'mgmtnetworks.MgmtNetConf',
        'app': 'mgmtnetworks',
        'admin_classes': (
            ('MgmtNetConfInline', 'address', '', 'content_object'),
        ),
        'get_addr': lambda obj: getattr(obj, 'addr'),
    }, {
        'model': 'tinc.Host',
        'app': 'tinc',
        'admin_classes': (
             ('HostAdmin', 'address', 'mgmt_net', ''),
        ),
        'get_addr': lambda obj: getattr(obj.mgmt_net, 'addr'),
        'schedule': 0, # disabled (handled by mgmtnetworks)
    }, {
        'model': 'slices.SliverIface',
        'app': 'slices',
        'admin_classes': (
            ('SliverIfaceInline', 'ipv6_addr', '', 'sliver'),
        ),
        'filter': {'type': 'management'},
        'get_addr': lambda obj: getattr(obj, 'ipv6_addr'),
    }
))

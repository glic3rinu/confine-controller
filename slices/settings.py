from django.conf import settings

ugettext = lambda s: s


CPU_REQUEST_CHOICES = getattr(settings, 'CPU_REQUEST_CHOICES', (
    ('weighted', 'Weighted'),
    ('reserved', 'Reserved'),
))
    
DEFAULT_CPU_REQUEST = getattr(settings, 'DEFAULT_CPU_REQUEST', 'weighted')

PUBLIC = 'public'
ISOLATED = 'isolated'

NETWORK_REQUESRT_CHOICES = getattr(settings, 'NETWORK_REQUESRT_CHOICES', (
    (PUBLIC, 'Public'),
    (ISOLATED, 'Isolated'),
#    ('passive', 'Passive'),
#    ('raw', 'RAW'),
))
    
DEFAULT_NETWORK_REQUEST = getattr(settings, 'DEFAULT_NETWORK_REQUEST', PUBLIC)

STORAGE_CHOICES = getattr(settings, 'STORAGE_CHOICES', (
   ('debian-squeeze-amd64', 'Debian Squeeze amd64'),
   ('openwrt-backfire-amd64', 'OpenWRT Backfire amd64'),))
    
DEFAULT_STORAGE = getattr(settings, 'DEFAULT_STORAGE', 'openwrt-backfire-amd64')


ALLOCATED = 'ALLOCATED'
DEPLOYED = 'DEPLOYED'
STARTED = 'STARTED'

STATE_CHOICES = getattr(settings, 'STATE_CHOICES', (
    (ALLOCATED, 'ALLOCATED'),
    (DEPLOYED, 'DEPLOYED'),
    (STARTED, 'STARTED'),
    
))

DEFAULT_SLICE_STATE = getattr(settings, 'DEFAULT_SLICE_STATE', ALLOCATED)
DEFAULT_SLIVER_STATE = getattr(settings, 'DEFAULT_SLICE_STATE', ALLOCATED)


CODE_DIR = getattr(settings, 'CODE_DIR', 'code') 
TEMPLATE_DIR = getattr(settings, 'TEMPLATE_DIR', '/home/controller/controller/media/templates')

MAC_PREFIX = getattr(settings, 'MAC_PREFIX', '06:ab')
IPV6_PREFIX = getattr(settings, 'IPV6_PREFIX', 'X:Y:Z')
IPV4_PREFIX = getattr(settings, 'IPV4_PREFIX', '192.168.157')


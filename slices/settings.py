from django.conf import settings
import os

ugettext = lambda s: s


CPU_REQUEST_CHOICES = getattr(settings, 'CPU_REQUEST_CHOICES', (
    ('weighted', 'Weighted'),
    ('reserved', 'Reserved'),
))
    
DEFAULT_CPU_REQUEST = getattr(settings, 'DEFAULT_CPU_REQUEST', 'weighted')

PUBLIC = 'public'
ISOLATED = 'isolated'
PRIVATE = 'private'

NETWORK_REQUESRT_CHOICES = getattr(settings, 'NETWORK_REQUESRT_CHOICES', (
    (PUBLIC, 'Public'),
    (ISOLATED, 'Isolated'),
    (PRIVATE, 'Private'),
#    ('passive', 'Passive'),
#    ('raw', 'RAW'),
))
    
DEFAULT_NETWORK_REQUEST = getattr(settings, 'DEFAULT_NETWORK_REQUEST', PUBLIC)

STORAGE_CHOICES = getattr(settings, 'STORAGE_CHOICES', (
   ('debian-squeeze-amd64', 'Debian Squeeze amd64'),
   ('openwrt-backfire-amd64', 'OpenWRT Backfire amd64'),))
    
DEFAULT_STORAGE = getattr(settings, 'DEFAULT_STORAGE', 'openwrt-backfire-amd64')


INSERTED = 'INSERTED'
ALLOCATED = 'ALLOCATED'
DEPLOYED = 'DEPLOYED'
STARTED = 'STARTED'

STATE_CHOICES = getattr(settings, 'STATE_CHOICES', (
    (INSERTED, 'INSERTED'),
    (ALLOCATED, 'ALLOCATED'),
    (DEPLOYED, 'DEPLOYED'),
    (STARTED, 'STARTED'),
    
))

DEFAULT_SLICE_STATE = getattr(settings, 'DEFAULT_SLICE_STATE', INSERTED)
DEFAULT_SLIVER_STATE = getattr(settings, 'DEFAULT_SLICE_STATE', INSERTED)


CODE_DIR = getattr(settings, 'CODE_DIR', 'code') 
TEMPLATE_DIR = getattr(settings, 'TEMPLATE_DIR', os.path.join(os.path.dirname(__file__), '../media/templates').replace('\\', '/'))

MAC_PREFIX = getattr(settings, 'MAC_PREFIX', '06:ab')
IPV6_PREFIX = getattr(settings, 'IPV6_PREFIX', 'X:Y:Z')
IPV4_PREFIX = getattr(settings, 'IPV4_PREFIX', '192.168.157')


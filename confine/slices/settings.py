from django.conf import settings

ugettext = lambda s: s


CPU_REQUEST_CHOICES = getattr(settings, 'CPU_REQUEST_CHOICES', (
    ('weighted', 'Weighted'),
    ('reserved', 'Reserved'),
))
    
DEFAULT_CPU_REQUEST = getattr(settings, 'DEFAULT_CPU_REQUEST', 'weighted')

NETWORK_REQUESRT_CHOICES = getattr(settings, 'NETWORK_REQUESRT_CHOICES', (
    ('isolated', 'Isolated'),
    ('passive', 'Passive'),
    ('raw', 'RAW'),
))
    
DEFAULT_NETWORK_REQUEST = getattr(settings, 'DEFAULT_NETWORK_REQUEST', 'public')


STORAGE_CHOICES = getattr(settings, 'STORAGE_CHOICES', (
   ('debian-squeeze-amd64', 'Debian Squeeze amd64'),
   ('openwrt-backfire-amd64', 'OpenWRT Backfire amd64'),))
    
DEFAULT_STORAGE = getattr(settings, 'DEFAULT_STORAGE', 'openwrt-backfire-amd64')


ONLINE = 'ONLINE'
OFFLINE = 'OFFLINE'

STATUS_CHOICES = getattr(settings, 'STATUS_CHOICES', (
    (ONLINE, 'ONLINE'),
    (OFFLINE, 'OFFLINE'),))

DEFAULT_SLICE_STATUS = getattr(settings, 'DEFAULT_SLICE_STATUS', ONLINE)
DEFAULT_SLIVER_STATUS = getattr(settings, 'DEFAULT_SLICE_STATUS', ONLINE)


CODE_DIR = getattr(settings, 'CODE_DIR', 'code') 

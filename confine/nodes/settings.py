from django.conf import settings

ugettext = lambda s: s

SERVER_TINC_IP = getattr(settings, 'SERVER_TINC_IP', '') 
SERVER_TINC_PORT = getattr(settings, 'SERVER_TINC_PORT', '') 
SERVER_URL = getattr(settings, 'SERVER_URL', '') 
SERVER_PUBLIC_KEY = getattr(settings, 'SERVER_PUBLIC_KEY', '') 


UCI_DIR = getattr(settings, 'UCI_DIR', 'uci') 

STORAGE_CHOICES = getattr(settings, 'STORAGE_CHOICES', (
   ('debian-squeeze-amd64', 'Debian Squeeze amd64'),
   ('openwrt-backfire-amd64', 'OpenWRT Backfire amd64'),))
    
DEFAULT_STORAGE = getattr(settings, 'DEFAULT_STORAGE', 'openwrt-backfire-amd64')    


ARCHITECTURE_CHOICES = getattr(settings, 'ARCHITECTURE_CHOICES', (
    ('x86_ep80579', 'x86_ep80579'),
    ('x86_generic', 'x86_generic'),
    ('brcm47xx', 'brcm47xx'),
    ('ar7', 'ar7'),
    ('ar71xx', 'ar71xx'),
    ('atheros', 'atheros'),
    ('au1000', 'au1000'),
    ('ppc40x', 'ppc40x'),
    ('ppc44x', 'ppc44x'),
    ('rb532', 'rb532'),))

DEFAULT_ARCHITECTURE = getattr(settings, 'DEFAULT_ARCHITECTURE', 'x86_generic')


ONLINE = 'ONLINE'
OFFLINE = 'OFFLINE'
PROJECTED = 'PROJECTED'
DISABLED = 'DISABLED'

NODE_STATUS_CHOICES = getattr(settings, 'NODE_STATUS_CHOICES', (
    (ONLINE, 'ONLINE'),
    (OFFLINE, 'OFFLINE'),
    (PROJECTED, 'PROJECTED'),
    (DISABLED, 'DISABLED'),))
    
DEFAULT_NODE_STATUS = getattr(settings, 'DEFAULT_NODEL_STATUS', ONLINE)


LINK_STATUS_CHOICES = getattr(settings, 'LINK_STATUS_CHOICES', (
    (ONLINE, 'ONLINE'),
    (OFFLINE, 'OFFLINE'),))

DEFAULT_LINK_STATUS = getattr(settings, 'DEFAULT_LINK_STATUS', ONLINE)

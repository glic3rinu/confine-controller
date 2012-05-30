from django.conf import settings

ugettext = lambda s: s

SERVER_TINC_IP = getattr(settings, 'SERVER_TINC_IP', '') 
SERVER_TINC_PORT = getattr(settings, 'SERVER_TINC_PORT', '') 
SERVER_URL = getattr(settings, 'SERVER_URL', '') 
SERVER_PUBLIC_KEY = getattr(settings, 'SERVER_PUBLIC_KEY', '')

SERVER_PRIVATE_KEY = getattr(settings, 'SERVER_PRIVATE_KEY', '') 
TESTBED_BASE_IP = getattr(settings, 'TESTBED_BASE_IP', '') 


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

NODE_STATE_CHOICES = getattr(settings, 'NODE_STATE_CHOICES', (
    (ONLINE, 'ONLINE'),
    (OFFLINE, 'OFFLINE'),
    (PROJECTED, 'PROJECTED'),
    (DISABLED, 'DISABLED'),))
    
DEFAULT_NODE_STATE = getattr(settings, 'DEFAULT_NODEL_STATE', ONLINE)

IFACE_TYPE_CHOICES = getattr(settings, 'IFACE_TYPE_CHOICES', (
    ('802.11a/b', '802.11a/b'),
    ('802.11a/b/g', '802.11a/b/g'),
    ('802.11a/b/g/n', '802.11a/b/g/n'),
    ('802.3u', 'Fast Ethernet 802.3z'),
    ('802.3z', 'Gigabit Ethernet 802.3z'),
    ('802.16', 'WiMax'),
))

DEFAULT_IFACE_TYPE = getattr(settings, 'DEFAULT_IFACE_TYPE', '802.11a/b/g/n')


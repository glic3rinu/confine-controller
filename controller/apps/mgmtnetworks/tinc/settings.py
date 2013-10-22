from django.conf import settings


TINC_PORT_DFLT = getattr(settings, 'TINC_PORT_DFLT', '655')

# TODO rename to tinc_tincd_conf
TINC_TINCD_ROOT = getattr(settings, 'TINC_TINCD_ROOT', '/etc/tinc')

TINC_NET_NAME = getattr(settings, 'TINC_NET_NAME', 'confine')

TINC_TINCD_BIN = getattr(settings, 'TINC_TINCD_BIN', '/usr/sbin/tincd')

TINC_TINCD_SEND_HUP = getattr(settings, 'TINC_TINCD_SEND_HUP', True)

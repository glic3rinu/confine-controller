from django.conf import settings

ugettext = lambda s: s

# TODO move to base_settings.py

# ConfineParams
DEBUG_IPV6_PREFIX = getattr(settings, 'DEBUG_IPV6_PREFIX', 'fd5f:eee5:a6ad::/48')
PRIV_IPV6_PREFIX = getattr(settings, 'PRIV_IPV6_PREFIX', 'aa5f:eee5:a6ad::/48')


# TestbedParams
PRIV_IPV4_PREFIX_DFLT = getattr(settings, 'PRIV_IPV4_PREFIX_DFLT', '192.168.157.0/24')
SLIVER_MAC_PREFIX_DFLT = getattr(settings, 'SLIVER_MAC_PREFIX_DFLT', '0x06ab')
MGMT_IPV6_PREFIX = getattr(settings, 'MGMT_IPV6_PREFIX', '2001:db8:cafe::/48')


# Disable CSRF on login form allowing integration with other services
DISABLE_LOGIN_CSRF_FROM = getattr(settings, 'DISABLE_LOGIN_CSRF_FROM', [])

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



CA_PRIV_KEY_PATH = getattr(settings, 'CA_PRIV_KEY_PATH', '/tmp/priv')
CA_PUB_KEY_PATH = getattr(settings, 'CA_PUB_KEY_PATH', '/tmp/pub')
CA_CERT_PATH = getattr(settings, 'CA_CERT_PATH', '/tmp/cert')
CA_CERT_EXP_DAYS = getattr(settings, 'CA_CERT_EXP_DAYS', 60*60*24*365*4)

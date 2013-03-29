from django.conf import settings

ugettext = lambda s: s

# absolute ath or relative to site_root
PKI_CA_PRIV_KEY_PATH = getattr(settings, 'PKI_CA_PRIV_KEY_PATH', 'pki/key.priv')
PKI_CA_PUB_KEY_PATH = getattr(settings, 'PKI_CA_PUB_KEY_PATH', 'pki/key.pub')
PKI_CA_CERT_PATH = getattr(settings, 'PKI_CA_CERT_PATH', 'pki/cert')

PKI_CA_CERT_EXP_DAYS = getattr(settings, 'PKI_CA_CERT_EXP_DAYS', 365*4)

PKI_DN_COUNTRY_DFLT = getattr(settings, 'PKI_DN_COUNTRY_DFLT', 'ES')
PKI_DN_STATE_DFLT = getattr(settings, 'PKI_DN_STATE_DFLT', 'Catalonia')
PKI_DN_LOCALITY_DFLT = getattr(settings, 'PKI_DN_LOCALITY_DFLT', 'Barcelona')
PKI_DN_ORG_NAME_DFLT = getattr(settings, 'PKI_DN_ORG_NAME_DFLT', 'Confine Project')
PKI_DN_ORG_UNIT_DFLT = getattr(settings, 'PKI_DN_ORG_UNIT_DFLT', 'Testbed Operation')

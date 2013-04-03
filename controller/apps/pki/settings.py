from django.conf import settings

ugettext = lambda s: s

PKI_CA_PRIV_KEY_PATH = getattr(settings, 'PKI_CA_PRIV_KEY_PATH', '%(site_root)s/ca/key.priv')
PKI_CA_PUB_KEY_PATH = getattr(settings, 'PKI_CA_PUB_KEY_PATH', '%(site_root)s/ca/key.pub')
PKI_CA_CERT_PATH = getattr(settings, 'PKI_CA_CERT_PATH', '%(site_root)s/ca/cert')

PKI_CA_CERT_EXP_DAYS = getattr(settings, 'PKI_CA_CERT_EXP_DAYS', 365*4)

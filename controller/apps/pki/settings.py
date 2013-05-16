from django.conf import settings


PKI_CA_PRIV_KEY_PATH = getattr(settings, 'PKI_CA_PRIV_KEY_PATH', '%(site_root)s/pki/key.priv')
PKI_CA_PUB_KEY_PATH = getattr(settings, 'PKI_CA_PUB_KEY_PATH', '%(site_root)s/pki/key.pub')
PKI_CA_CERT_PATH = getattr(settings, 'PKI_CA_CERT_PATH', '%(site_root)s/pki/cert')

PKI_CA_CERT_EXP_DAYS = getattr(settings, 'PKI_CA_CERT_EXP_DAYS', 365*4)

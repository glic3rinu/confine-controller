import os

from django.conf import settings


# Certificate Authority bundle for validating the CNDB connection certificate
COMMUNITYNETWORKS_CNDB_CA_BUNDLE = getattr(settings, 'COMMUNITYNETWORKS_CNDB_CA_BUNDLE',
    os.path.join(os.path.dirname(__file__), 'certs/cacert.org.pem'))

# CNDB auth system url
COMMUNITYNETWORKS_CNDB_URL_AUTH = getattr(settings,'COMMUNITYNETWORKS_CNDB_URL_AUTH',
    'https://ffm.gg32.com/RAT')

# CNDB credentials
COMMUNITYNETWORKS_CNDB_USER = getattr(settings,'COMMUNITYNETWORKS_CNDB_USER', '')
COMMUNITYNETWORKS_CNDB_PASS = getattr(settings,'COMMUNITYNETWORKS_CNDB_PASS', '')

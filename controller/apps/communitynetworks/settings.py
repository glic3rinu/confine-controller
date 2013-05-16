import os

from django.conf import settings


# Certificate Authority bundle for validating the CNDB connection certificate
COMMUNITYNETWORKS_CNDB_CA_BUNDLE = getattr(settings, 'COMMUNITYNETWORKS_CNDB_CA_BUNDLE',
    os.path.join(os.path.dirname(__file__), 'certs/cacert.org.pem'))


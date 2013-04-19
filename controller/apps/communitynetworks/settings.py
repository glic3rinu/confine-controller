import os

from django.conf import settings


# Certificate Authority bundle for validating the CNDB connection certificate
# ca_bundle='/etc/ssl/certs/cacert.org.pem'
module_dir = os.path.dirname(__file__) 
ca_bundle = os.path.join(module_dir, 'certs/cacert.org.pem')
COMMUNITYNETWORKS_CNDB_CA_BUNDLE = getattr(settings, 'COMMUNITYNETWORKS_CNDB_CA_BUNDLE', ca_bundle)


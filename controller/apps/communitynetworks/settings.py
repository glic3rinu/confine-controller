import os

from django.conf import settings

# another approach to get app path
# http://blog.elsdoerfer.name/2008/06/06/django-finding-the-current-projects-path/
module_dir = os.path.dirname(__file__) 

# Certificate Authority bundle for validating the CNDB connection certificate
# ca_bundle='/etc/ssl/certs/cacert.org.pem'
ca_bundle = os.path.join(module_dir, 'certs/cacert.org.pem')
COMMUNITYNETWORKS_CNDB_CA_BUNDLE = getattr(settings, 'COMMUNITYNETWORKS_CNDB_CA_BUNDLE', ca_bundle)


from django.conf import settings

from controller.utils.paths import get_site_root


MAINTENANCE_KEY_PATH = getattr(settings, 'MAINTENANCE_KEY_PATH',
    '%(site_root)s/pki/maintenance_rsa'  % { 'site_root': get_site_root() })

MAINTENANCE_PUB_KEY_PATH = getattr(settings, 'MAINTENANCE_PUB_KEY_PATH',
    '%(site_root)s/pki/maintenance_rsa.pub' % { 'site_root': get_site_root() })

from django.conf import settings


ugettext = lambda s: s


MAINTENANCE_KEY_PATH = getattr(settings, 'MAINTENANCE_KEY_PATH', '/home/confine/communitylab/id_rsa')

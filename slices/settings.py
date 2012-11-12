from celery.task.schedules import crontab
from datetime import timedelta
from django.conf import settings


ugettext = lambda s: s


TEMPLATE_TYPES = getattr(settings, 'TEMPLATE_TYPES', (
    ('debian6', 'Debian 6'), 
    ('fedora12', 'Fedora 12'), 
    ('susele6', 'SUSE Linux Enterprise 6'),
))

DEFAULT_TEMPLATE_TYPE = getattr(settings, 'DEFAULT_TEMPLATE_TYPE', 'debian6')


TEMPLATE_ARCHS = getattr(settings, 'TEMPLATE_ARCHS', (
    ('amd64', 'amd64'), 
    ('ia64', 'ia64'), 
    ('x86', 'x86'),
))

DEFAULT_TEMPLATE_ARCH = getattr(settings, 'DEFAULT_TEMPLATE_ARCH', 'amd64')


TEMPLATE_IMAGE_DIR = getattr(settings, 'TEMPLATE_IMAGE_DIR', 'templates/')
SLICE_EXP_DATA_DIR = getattr(settings, 'SLICE_EXP_DATA_DIR', 'exp_data/')


# 30 days expiration interval
SLICE_EXPIRATION_INTERVAL = getattr(settings, 'SLICE_EXPIRATION_INTERVAL', timedelta(30))

# Clean expired slices everyday at midnigth
CLEAN_EXPIRED_SLICES_CRONTAB = getattr(settings, 'CLEAN_EXPIRED_SLICES_CRONTAB',
    crontab(minute=0, hour=0))

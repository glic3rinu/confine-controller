from celery.task.schedules import crontab
from datetime import timedelta
from django.conf import settings


ugettext = lambda s: s


SLICES_TEMPLATE_TYPES = getattr(settings, 'SLICES_TEMPLATE_TYPES', (
    ('debian6', 'Debian 6'), 
    ('fedora12', 'Fedora 12'), 
    ('susele6', 'SUSE Linux Enterprise 6'),
))

SLICES_TEMPLATE_TYPE_DFLT = getattr(settings, 'SLICES_TEMPLATE_TYPE_DFLT', 'debian6')


SLICES_TEMPLATE_ARCHS = getattr(settings, 'SLICES_TEMPLATE_ARCHS', (
    ('amd64', 'amd64'), 
    ('ia64', 'ia64'), 
    ('x86', 'x86'),
))

SLICES_TEMPLATE_ARCH_DFLT = getattr(settings, 'SLICES_TEMPLATE_ARCH_DFLT', 'amd64')


SLICES_TEMPLATE_IMAGE_DIR = getattr(settings, 'SLICES_TEMPLATE_IMAGE_DIR', 'templates/')
SLICES_SLICE_EXP_DATA_DIR = getattr(settings, 'SLICES_SLICE_EXP_DATA_DIR', 'exp_data/')


# 30 days expiration interval
SLICES_SLICE_EXP_INTERVAL = getattr(settings, 'SLICES_SLICE_EXP_INTERVAL', timedelta(30))
SLICES_SLICE_EXP_WARN_INTERVAL = getattr(settings, 'SLICES_SLICE_EXP_WARN_INTERVAL', timedelta(4))

# Clean expired slices everyday at midnigth
SLICES_CLEAN_EXP_SLICE_CRONTAB = getattr(settings, 'CLEAN_EXP_SLICE_CRONTAB',
    crontab(minute=0, hour=0))

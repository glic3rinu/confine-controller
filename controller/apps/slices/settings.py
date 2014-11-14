import warnings
from datetime import timedelta

from django.conf import settings


SLICES_TEMPLATE_TYPES = getattr(settings, 'SLICES_TEMPLATE_TYPES', (
        ('debian', 'Debian'),
        ('openwrt', 'OpenWRT'),
))

SLICES_TEMPLATE_TYPE_DFLT = getattr(settings, 'SLICES_TEMPLATE_TYPE_DFLT', '')


SLICES_TEMPLATE_ARCHS = getattr(settings, 'SLICES_TEMPLATE_ARCHS', (
        ('amd64', 'amd64'),
        ('x86', 'x86'),
))

SLICES_TEMPLATE_ARCH_DFLT = getattr(settings, 'SLICES_TEMPLATE_ARCH_DFLT', '')

SLICES_TEMPLATE_IMAGE_DIR = getattr(settings, 'SLICES_TEMPLATE_IMAGE_DIR', 'templates')

SLICES_TEMPLATE_IMAGE_NAME = getattr(settings, 'SLICES_TEMPLATE_IMAGE_NAME', '')

SLICES_TEMPLATE_IMAGE_EXTENSIONS = getattr(settings, 'SLICES_TEMPLATE_IMAGE_EXTENSIONS',
        ('.tar.gz', '.tgz'))

SLICES_SLICE_DATA_DIR = getattr(settings, 'SLICES_SLICE_DATA_DIR',
        getattr(settings, 'SLICES_SLICE_EXP_DATA_DIR', 'exp_data'))

SLICES_SLICE_DATA_NAME = getattr(settings, 'SLICES_SLICE_DATA_NAME',
        getattr(settings, 'SLICES_SLICE_EXP_DATA_NAME', 'slice-%(pk)d-%(original)s'))

SLICES_SLIVER_DATA_DIR = getattr(settings, 'SLICES_SLIVER_DATA_DIR',
        getattr(settings, 'SLICES_SLIVER_EXP_DATA_DIR', 'exp_data'))

SLICES_SLIVER_DATA_NAME = getattr(settings, 'SLICES_SLIVER_DATA_NAME',
        getattr(settings, 'SLICES_SLIVER_EXP_DATA_NAME', 'sliver-%(pk)d-%(original)s'))


# 30 days expiration interval
SLICES_SLICE_EXP_INTERVAL = getattr(settings, 'SLICES_SLICE_EXP_INTERVAL', timedelta(days=30))
# Send warning email 4 days before expiration
SLICES_SLICE_EXP_WARN = getattr(settings, 'SLICES_SLICE_EXP_WARN', timedelta(days=4))

# List of disabled sliver ifaces. i.e. ['management', 'public4']
SLICES_DISABLED_SLIVER_IFACES = getattr(settings, 'SLICES_DISABLED_SLIVER_IFACES', [])

# Warn user of settings rename on #234
# TODO: *_EXP_DATA_* settings will be removed on 0.11.1 (not backwards compatibility)
for value in ['SLICES_SLICE_EXP_DATA_DIR', 'SLICES_SLICE_EXP_DATA_NAME',
    'SLICES_SLIVER_EXP_DATA_NAME', 'SLICES_SLIVER_EXP_DATA_DIR']:
    if hasattr(settings, value):
        new_value = value.replace('EXP_DATA', 'DATA')
        warnings.warn("'%s' setting has been renamed to '%s' (see #234)." %
            (value, new_value), DeprecationWarning)

# Warn user of removed settings on #200
# TODO: remove this warning on v0.12
for value in ['SLICES_SLICE_OVERLAY_DIR', 'SLICES_SLICE_OVERLAY_NAME',
              'SLICES_SLIVER_OVERLAY_DIR', 'SLICES_SLIVER_OVERLAY_NAME',
              'SLICES_SLIVER_OVERLAY_EXTENSIONS']:
    if hasattr(settings, value):
        warnings.warn("'%s' setting has been removed (see #200)." % value)

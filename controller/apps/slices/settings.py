from datetime import timedelta

from django.conf import settings


SLICES_TEMPLATE_TYPES = getattr(settings, 'SLICES_TEMPLATE_TYPES', (
        ('debian', 'Debian'),
        ('openwrt', 'OpenWRT'),
))

SLICES_TEMPLATE_TYPE_DFLT = getattr(settings, 'SLICES_TEMPLATE_TYPE_DFLT', 'debian6')


SLICES_TEMPLATE_ARCHS = getattr(settings, 'SLICES_TEMPLATE_ARCHS', (
        ('amd64', 'amd64'),
        ('x86', 'x86'),
))

SLICES_TEMPLATE_ARCH_DFLT = getattr(settings, 'SLICES_TEMPLATE_ARCH_DFLT', 'x86')

SLICES_TEMPLATE_IMAGE_DIR = getattr(settings, 'SLICES_TEMPLATE_IMAGE_DIR', 'templates')

SLICES_TEMPLATE_IMAGE_NAME = getattr(settings, 'SLICES_TEMPLATE_IMAGE_NAME', '')

SLICES_TEMPLATE_IMAGE_EXTENSIONS = getattr(settings, 'SLICES_TEMPLATE_IMAGE_EXTENSIONS',
        ('.tar.gz', '.tgz'))

SLICES_SLICE_EXP_DATA_DIR = getattr(settings, 'SLICES_SLICE_EXP_DATA_DIR', 'exp_data')

SLICES_SLICE_EXP_DATA_NAME = getattr(settings, 'SLICES_SLICE_EXP_DATA_NAME',
        'slice-%(pk)d-%(original)s')

SLICES_SLICE_EXP_DATA_EXTENSIONS = getattr(settings, 'SLICES_SLICE_EXP_DATA_EXTENSIONS',
        ('.tar.gz', '.tgz'))

SLICES_SLICE_OVERLAY_DIR = getattr(settings, 'SLICES_SLICE_OVERLAY_DIR', 'overlay')

SLICES_SLICE_OVERLAY_NAME = getattr(settings, 'SLICES_SLICE_OVERLAY_NAME',
        'slice-%(pk)d-%(original)s')

SLICES_SLICE_OVERLAY_EXTENSIONS = getattr(settings, 'SLICES_SLICE_OVERLAY_EXTENSIONS',
        ('.tar.gz', '.tgz'))

SLICES_SLIVER_EXP_DATA_DIR = getattr(settings, 'SLICES_SLIVER_EXP_DATA_DIR', 'exp_data')

SLICES_SLIVER_EXP_DATA_NAME = getattr(settings, 'SLICES_SLIVER_EXP_DATA_NAME',
        'sliver-%(pk)d-%(original)s')

SLICES_SLIVER_EXP_DATA_EXTENSIONS = getattr(settings, 'SLICES_SLIVER_EXP_DATA_EXTENSIONS',
        ('.tar.gz', '.tgz'))

SLICES_SLIVER_OVERLAY_DIR = getattr(settings, 'SLICES_SLICE_OVERLAY_DIR', 'overlay')

SLICES_SLIVER_OVERLAY_NAME = getattr(settings, 'SLICES_SLICE_EXP_DATA_NAME',
        'slice-%(pk)d-%(original)s')

SLICES_SLIVER_OVERLAY_EXTENSIONS = getattr(settings, 'SLICES_SLICE_EXP_DATA_EXTENSIONS',
        ('.tar.gz', '.tgz'))


# 30 days expiration interval
SLICES_SLICE_EXP_INTERVAL = getattr(settings, 'SLICES_SLICE_EXP_INTERVAL', timedelta(days=30))
# Send warning email 4 days before expiration
SLICES_SLICE_EXP_WARN = getattr(settings, 'SLICES_SLICE_EXP_WARN', timedelta(days=4))

# List of disabled sliver ifaces. i.e. ['management', 'public4']
SLICES_DISABLED_SLIVER_IFACES = getattr(settings, 'SLICES_DISABLED_SLIVER_IFACES', [])

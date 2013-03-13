import os
from datetime import timedelta

from django.conf import settings


ugettext = lambda s: s


SLICES_TEMPLATE_TYPES = getattr(settings, 'SLICES_TEMPLATE_TYPES', (
    ('debian6', 'Debian 6'),
    ('openwrt-backfire', 'OpenWRT Backfire'),
))

SLICES_TEMPLATE_TYPE_DFLT = getattr(settings, 'SLICES_TEMPLATE_TYPE_DFLT', 'debian6')


SLICES_TEMPLATE_ARCHS = getattr(settings, 'SLICES_TEMPLATE_ARCHS', (
    ('amd64', 'amd64'),
    ('ia64', 'ia64'),
    ('x86', 'x86'),
))

SLICES_TEMPLATE_ARCH_DFLT = getattr(settings, 'SLICES_TEMPLATE_ARCH_DFLT', 'x86')

SLICES_TEMPLATE_IMAGE_DIR = getattr(settings, 'SLICES_TEMPLATE_IMAGE_DIR', 'templates')

SLICES_TEMPLATE_IMAGE_NAME = getattr(settings, 'SLICES_TEMPLATE_IMAGE_NAME', 'template-%(rand)s.squashfs')

SLICES_SLICE_EXP_DATA_DIR = getattr(settings, 'SLICES_SLICE_EXP_DATA_DIR', 'exp_data')

SLICES_SLICE_EXP_DATA_NAME = getattr(settings, 'SLICES_SLICE_EXP_DATA_NAME', 'slice-experiment-%(rand)s.data')

SLICES_SLIVER_EXP_DATA_DIR = getattr(settings, 'SLICES_SLIVER_EXP_DATA_DIR', 'exp_data')

SLICES_SLIVER_EXP_DATA_NAME = getattr(settings, 'SLICES_SLIVER_EXP_DATA_NAME', 'sliver-experiment-%(rand)s.data')


# 30 days expiration interval
SLICES_SLICE_EXP_INTERVAL = getattr(settings, 'SLICES_SLICE_EXP_INTERVAL', timedelta(30))
# Send warning email 4 days before expiration
SLICES_SLICE_EXP_WARN_DAYS = getattr(settings, 'SLICES_SLICE_EXP_WARN_DAYS', 4)

# List of disabled sliver ifaces. i.e. ['management', 'public4']
SLICES_DISABLED_SLIVER_IFACES = getattr(settings, 'SLICES_DISABLED_SLIVER_IFACES', [])

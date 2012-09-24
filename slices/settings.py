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


TEMPLATE_DATA_DIR = getattr(settings, 'TEMPLATE_DATA_DIR', 'templates/')
SLICE_EXP_DATA_DIR = getattr(settings, 'SLICE_EXP_DATA_DIR', 'exp_data/')

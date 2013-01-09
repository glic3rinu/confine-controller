from django.conf import settings
from django.utils.importlib import import_module


def autodiscover(module):
    """ Auto-discover INSTALLED_APPS permission.py module """
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        try: 
            import_module('%s.%s' % (app, module))
        except ImportError, e:
            # Hack for preventing mask of import errors
            if str(e) != 'No module named %s' % module:
                raise

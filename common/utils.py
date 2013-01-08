from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def autodiscover(module):
    """ Auto-discover INSTALLED_APPS permission.py module """
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        try: 
            import_module('%s.%s' % (app, module))
        except (ImportError, ImproperlyConfigured): 
            pass


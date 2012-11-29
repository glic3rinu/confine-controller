from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

from .permissions import Permission, ReadOnlyPermission


# Autodiscover permissions.py
def autodiscover():
    """ Auto-discover INSTALLED_APPS permission.py module """
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        try: 
            import_module('%s.permissions' % app)
        except (ImportError, ImproperlyConfigured): 
            pass

autodiscover()

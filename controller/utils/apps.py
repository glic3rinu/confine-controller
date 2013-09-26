"""
    Define app dependencies tree for better add/remove INSTALLED_APP
    Attribution note: source of _try_import of django-app-dependecies
    thanks to adammck at https://github.com/adammck/django-app-dependencies/
"""

import sys


class DependencyImportError(ImportError):
    pass


def _try_import(module_name):
    """
        Attempts to import and return *module_name*, returning None if an
        ImportError was raised. Unlike the standard try/except approach to
        optional imports, this method jumps through some hoops to avoid
        catching ImportErrors raised from within *module_name*.
        
          # import a module from the python
          # stdlib. this should always work
          >>> _try_import("csv") # doctest: +ELLIPSIS
          <module 'csv' from '...'>
          
          # attempt to import a module that
          # doesn't exist; no exception raised
          >>> _try_import("spam.spam.spam") is None
          True
    """
    
    try:
        __import__(module_name)
        return sys.modules[module_name]
    except ImportError:
        # extract a backtrace, so we can find out where the exception was
        # raised from. if there is a NEXT frame, it means that the import
        # statement succeeded, but an ImportError was raised from _within_
        # the imported module. we must allow this error to propagate, to
        # avoid silently masking it with this optional import
        traceback = sys.exc_info()[2]
        if traceback.tb_next:
            raise
        # otherwise, the exception was raised
        # from this scope. *module_name* couldn't
        # be imported,which isn't such a big deal
        return None


def app_dependencies(app):
    """ Get the app dependencies """
    module = _try_import(app)
    if module is None:
        raise DependencyImportError("No module named '%s'" % (app))
    req_apps = ['controller'] # All depend on the controller
    if hasattr(module, "REQUIRED_APPS"):
        req_apps += module.REQUIRED_APPS
    return req_apps


def is_installed(app):
    """ returns True if app is installed """
    from django.conf import settings
    return app in settings.INSTALLED_APPS


def add_app(INSTALLED_APPS, app):
    """ add app to installed_apps satisfying dependencies """
    if app in INSTALLED_APPS:
        return INSTALLED_APPS
    
    apps = list(INSTALLED_APPS)
    index = 0
    for dependency in app_dependencies(app):
        if not dependency in apps:
            apps = list(add_app(apps, dependency))
        index = max(index, apps.index(dependency) + 1) # insert after last dependency
    apps.insert(index, app)
    return tuple(apps)


def remove_app(INSTALLED_APPS, app):
    """ remove app from installed_apps """
    if app in INSTALLED_APPS:
        apps = list(INSTALLED_APPS)
        apps.remove(app)
        return tuple(apps)
    return INSTALLED_APPS

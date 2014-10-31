from __future__ import absolute_import

import os
import re
import time
import warnings
from distutils.sysconfig import get_python_lib
from urlparse import urlparse

from django.core.mail import EmailMultiAlternatives
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from controller.core.exceptions import OperationLocked
from controller.utils.paths import get_project_root
from controller.utils.system import run, touch


# TODO split this shit inot different modules in order to avoid import issues
#      when imported from settings.py

def autodiscover(module):
    """ Auto-discover INSTALLED_APPS module.py """
    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        try: 
            import_module('%s.%s' % (app, module))
        except ImportError:
            # Decide whether to bubble up this error. If the app just
            # doesn't have the module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, module):
                print '%s module caused this error:' % module
                raise


def decode_version(version):
    """
    Reverse operation of controller get_version
    Converts a string formated version into a three integer
    tuple (major, major2, minor). E.g. (1, 1, 3)
    
    """
    version_re = re.compile(r'^\s*(\d+)\.(\d+)\.(\d+).*')
    minor_release = version_re.search(version)
    if minor_release is not None:
        major, major2, minor = version_re.search(version).groups()
    else:
        version_re = re.compile(r'^\s*(\d+)\.(\d+).*')
        if version_re.search(version) is not None:
            major, major2 = version_re.search(version).groups()
            minor = 0
        else:
            raise ValueError('Invalid controller version string "%s".' % version)
    return int(major), int(major2), int(minor)


def is_installed(app):
    """ returns True if app is installed """
    from .apps import is_installed
    warnings.warn("Deprecated: use controller.utils.apps.is_installed", DeprecationWarning)
    is_installed(app)


def add_app(INSTALLED_APPS, app, prepend=False, append=True):
    """ add app to installed_apps """
    from .apps import add_app
    warnings.warn("Deprecated: use controller.utils.apps.add_app", DeprecationWarning)
    return add_app(INSTALLED_APPS, app)


def remove_app(INSTALLED_APPS, app):
    """ remove app from installed_apps """
    from .apps import remove_app
    warnings.warn("Deprecated: use controller.utils.apps.remove_app", DeprecationWarning)
    return remove_app(INSTALLED_APPS, app)


def get_controller_site():
    """ 
    Returns a site-like object based on SITE_URL setting than can be used on templates
    """
    # Avoid import problems ...
    from controller import settings as controller_settings
    url = urlparse(controller_settings.SITE_URL)
    return {
        'domain': url.netloc,
        'name': controller_settings.SITE_NAME,
        'scheme': url.scheme
    }


def send_email_template(template, context, to, email_from=None, html=None):
    """
    Renders an email template with this format:
        {% if subject %}Subject{% endif %}
        {% if message %}Email body{% endif %}
    
    context can be a dictionary or a template.Context instance
    """
    from django.template.loader import render_to_string
    from django.template import Context
    if isinstance(context, dict):
        context = Context(context)
    if type(to) in [str, unicode]:
        to = [to]
    
    if not 'site' in context: # fallback site value
        context.update({'site': get_controller_site()})
    
    #subject cannot have new lines
    subject = render_to_string(template, {'subject': True}, context).strip()
    message = render_to_string(template, {'message': True}, context)
    msg = EmailMultiAlternatives(subject, message, email_from, to)
    if html:
        html_message = render_to_string(html, {'message': True}, context)
        msg.attach_alternative(html_message, "text/html")
    msg.send()


def get_existing_pip_installation():
    """ returns current pip installation path """
    if run("pip freeze|grep confine-controller", err_codes=[0,1]).return_code == 0:
        for lib_path in get_python_lib(), get_python_lib(prefix="/usr/local"):
            existing_path = os.path.abspath(os.path.join(lib_path, "controller"))
            if os.path.exists(existing_path):
                return existing_path
    return None


def update_settings(monkey_patch=None, **options):
    """ Warning this only works with a very simple setting format: NAME = value """
    from django.conf import settings
    for name, value in options.iteritems():
        if getattr(settings, name, None) != value:
            settings_file = os.path.join(get_project_root(), 'settings.py')
            context = {
                'name': name,
                'value': value if not isinstance(value, basestring) else "'%s'" % value,
                'settings': settings_file,
            }
            if run("grep '^%(name)s *=' %(settings)s" % context, err_codes=[0,1]):
                # Update existing settings_file
                run("sed -i \"s#%(name)s *=.*#%(name)s = %(value)s#\" %(settings)s" % context)
            else:
                run("echo \"%(name)s = %(value)s\" >> %(settings)s" % context)
            # Monkeypatch controller settings to make available the change globally
            if monkey_patch is not None:
                module = import_module(monkey_patch)
                setattr(module, name, value)


class LockFile(object):
    """ File-based lock mechanism used for preventing concurrency problems """
    def __init__(self, lockfile, expire=5*60, unlocked=False):
        """ /dev/shm/ can be a good place for storing locks ;) """
        self.lockfile = lockfile
        self.expire = expire
        self.unlocked = unlocked
    
    def acquire(self):
        if os.path.exists(self.lockfile):
            lock_time = os.path.getmtime(self.lockfile)
            # lock expires to avoid starvation
            if time.time()-lock_time < self.expire:
                return False
        touch(self.lockfile)
        return True
    
    def release(self):
        os.remove(self.lockfile)
    
    def __enter__(self):
        if not self.unlocked:
            if not self.acquire():
                raise OperationLocked('%s lock file exists and its mtime is less '
                    'than %s seconds' % (self.lockfile, self.expire))
        return True
    
    def __exit__(self, type, value, traceback):
        if not self.unlocked:
            self.release()

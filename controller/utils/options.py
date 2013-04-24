import os, time
from distutils.sysconfig import get_python_lib

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.template import Context
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from controller.core.exceptions import OperationLocked
from controller.utils.system import run, touch


def autodiscover(module):
    """ Auto-discover INSTALLED_APPS module.py """
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


def is_installed(app):
    """ returns True if app is installed """
    return app in settings.INSTALLED_APPS


def add_app(INSTALLED_APPS, app, prepend=False, append=True):
    """ add app to installed_apps """
    if app not in INSTALLED_APPS:
        if prepend:
            return (app,) + INSTALLED_APPS
        else:
            return INSTALLED_APPS + (app,)
    return INSTALLED_APPS


def remove_app(INSTALLED_APPS, app):
    """ remove app from installed_apps """
    if app in INSTALLED_APPS:
        apps = list(INSTALLED_APPS)
        apps.remove(app)
        return tuple(apps)
    return INSTALLED_APPS


def send_email_template(template, context, to, email_from=None):
    """
    Renders an email template with this format:
        {% if subject %}Subject{% endif %}
        {% if message %}Email body{% endif %}
    
    context can be a dictionary or a template.Context instance
    """
    if type(context) is dict:
        context = Context(context)
    if type(to) is str or type(to) is unicode:
        to = [to] #send_mail 'to' argument must be a list or a tuple
    
    from controller import settings as controller_settings
    email_context = {'site': controller_settings.SITE_URL}
    email_context.update(context)
    #subject cannot have new lines
    subject = render_to_string(template, {'subject': True}, email_context).strip()
    message = render_to_string(template, {'message': True}, email_context)
    send_mail(subject, message, email_from, to)


def get_existing_pip_installation():
    """ returns current pip installation path """
    if run("pip freeze|grep confine-controller", err_codes=[0,1]).return_code == 0:
        for lib_path in get_python_lib(), get_python_lib(prefix="/usr/local"):
            existing_path = os.path.abspath(os.path.join(lib_path, "controller"))
            if os.path.exists(existing_path):
                return existing_path
    return None


def update_settings(monkey_patch=None, **options):
    """ Warning this only works with a very simple setting format: NAME = 'value' """
    for name, value in options.iteritems():
        if getattr(settings, name, None) != value:
            settings_file = os.path.join(get_project_root(), 'settings.py')
            context = {
                'name': name,
                'value': value,
                'settings': settings_file,}
            if run("grep '%(name)s' %(settings)s" % context, err_codes=[0,1]):
                # Update existing settings_file
                run("sed -i \"s#%(name)s = *'.*' *#%(name)s = '%(value)s'#\" %(settings)s" % context)
            else:
                run("echo \"%(name)s = '%(value)s'\" >> %(settings)s" % context)
            # Monkeypatch controller settings to make available the change globally
            if monkey_patch is not None:
                module = import_module(monkey_patch)
                setattr(module, name, value)


class LockFile(object):
    """ File-based lock mechanism used for preventing concurrency problems """
    def __init__(self, lockfile, expire=5*60):
        """ /dev/shm/ can be a good place for storing locks ;) """
        self.lockfile = lockfile
        self.expire = expire
    
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
        if not self.acquire():
            raise OperationLocked('%s lock file exists and its mtime is less '
                'than %s seconds' % (self.lockfile, self.expire))
        return True
    
    def __exit__(self, type, value, traceback):
        self.release()

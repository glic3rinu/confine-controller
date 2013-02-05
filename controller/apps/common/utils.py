import os

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.template import Context
from django.utils.importlib import import_module

from .system import run


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


def is_installed(app):
    """ returns True if app is installed """
    return app in settings.INSTALLED_APPS


def send_mail_template(template, context, to, email_from=None):
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
    
    #subject cannot have new lines
    subject = render_to_string(template, {'subject': True}, context).strip()
    message = render_to_string(template, {'message': True}, context)
    send_mail(subject, message, email_from, to)


def get_project_root():
    """ Return the django project path """
    return os.path.dirname(os.path.normpath(os.sys.modules[settings.SETTINGS_MODULE].__file__))


def get_project_name():
    return os.path.basename(get_project_root())


def get_site_root():
    return os.path.abspath(os.path.join(get_project_root(), '..'))


def update_settings(**options):
    for name, value in options.iteritems():
        if getattr(settings, name, None) != value:
            settings_file = os.path.join(get_project_root(), 'settings.py')
            if run("grep '%s' %s" % (name, settings_file), err_codes=[0,1]):
                # Update existing settings_file
                run("""sed -i "s/%s = '\w*'/%s = '%s'/" %s""" % (name, name, value, settings_file))
            else:
                run("""echo "%s = '%s'" >> %s""" % (name, value, settings_file))

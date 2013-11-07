import os, sys

CONTROLLER_ROOT = os.path.dirname(os.path.realpath(__file__))
CONTROLLER_ROOT = os.path.abspath(os.path.join(CONTROLLER_ROOT, '..'))
sys.path.insert(0, os.path.join(CONTROLLER_ROOT, 'apps'))


# Django settings for controller project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'controller',      # Or path to database file if using sqlite3.
        'USER': 'confine',         # Not used with sqlite3.
        'PASSWORD': 'confine',     # Not used with sqlite3.
        'HOST': 'localhost',       # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                # Set to empty string for default. Not used with sqlite3.
    }
}

# Enable persistent connections
CONN_MAX_AGE = 60*10

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

ALLOWED_HOSTS = '*'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'state.middlewares.NodePullHeartBeat',
)

TEMPLATE_CONTEXT_PROCESSORS =(
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "controller.core.context_processors.site",
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    # confine-controller apps
    'controller',
    'api',
    'nodes',
    'slices',
    'issues',
    'state',
    'pings',
    'mgmtnetworks.tinc',
#    'sfa',
    'communitynetworks',
    'firmware',
#    'groupregistration',
    'gis',
    'users',
    'pki',
    'maintenance',
    'notifications',
    'monitor',
    
    # Third-party apps
    'south',
    'django_extensions',
    'djcelery',
    'djcelery_email',
    'privatefiles',
    'registration',
    'captcha', 
    'django_google_maps',
    'rest_framework',
    'rest_framework.authtoken',
    'fluent_dashboard',
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    
    # Django.contrib
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    
    # confine-controller apps that should load last
    'permissions', # because of overriding admin templates
)

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'permissions.auth.TestbedPermissionBackend',
    'users.auth.EmailBackend',
]

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Email config
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

# Storage configuration
DEFAULT_FILE_STORAGE = 'controller.core.storage.DoubleExtensionAwareFileSystemStorage'


#################################
## 3RD PARTY APPS CONIGURATION ##
#################################

# Admin Tools
ADMIN_TOOLS_MENU = 'controller.menu.CustomMenu'

# Fluent dashboard
ADMIN_TOOLS_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentIndexDashboard'
FLUENT_DASHBOARD_ICON_THEME = '../controller/icons'

FLUENT_DASHBOARD_APP_GROUPS = (
    ('Nodes', {
        'models': (
            'nodes.*',
        ),
        'collapsible': True,
    }),
    ('Slices', {
        'models': (
            'slices.*',
        ),
        'collapsible': True,
    }),
    ('Administration', {
        'models': (
            'users.models.User',
            'users.models.Group',
            'issues.models.Ticket',
            'djcelery.models.TaskState',
            'firmware.models.Config',
            'maintenance.models.Operation',
            'notifications.models.Notification',
        ),
        'collapsible': True,
    }),
    ('Tinc', {
        'models': (
            'mgmtnetworks.tinc.*',
        ),
        'collapsible': True,
    }),
)

FLUENT_DASHBOARD_APP_ICONS = {
    'users/user': "Mr-potato.png",
    'users/permission': "Locked.png",
    'users/group': "research_group.png",
    'nodes/node': "linksys-WRT54G.png",
    'nodes/server': "poweredge_r510.png",
    'nodes/researchdevice': "western-digital-mybook-pro.png",
    'slices/slice': "ChemSlice.png",
    'slices/sliver': "LXCBox2.png",
    'slices/template': "Application-x-gerber.png",
    'tinc/gateway': "Network.png",
    'tinc/island': "Weather-overcast.png",
    'tinc/tincaddress': "X-office-address-book.png",
    'tinc/host': "computer-dell-dimension-E521.png",
    'issues/ticket': "Ticket_star.png",
    'djcelery/taskstate': "taskstate.png",
    'firmware/config': "Firmware.png",
    'maintenance/operation': "gnome-terminal.png",
    'notifications/notification': "notifications.png",
}


## django-celery
import djcelery
djcelery.setup_loader()
# Broker
BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_SEND_EVENTS = True
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_DISABLE_RATE_LIMITS = True
# Do not fill the logs with crap
CELERY_REDIRECT_STDOUTS_LEVEL = 'DEBUG'
# gevent crashes after a broker timeout is reached, so better keep it disabled
BROKER_CONNECTION_TIMEOUT = None
# Send error alerts to admins
#CELERY_SEND_TASK_ERROR_EMAILS = True
# Use controller logging system instead of celery
#CELERYD_HIJACK_ROOT_LOGGER = False
#CELERY_SEND_TASK_ERROR_EMAILS = True
# Route state tasks to avoid gevent polluting other tasks
CELERY_ROUTES = {
         'state.node': {'queue': 'gevent'},
         'state.sliver': {'queue': 'gevent'},
         'state.get_state': {'queue': 'gevent'},
},
## end

# django-private-files
FILE_PROTECTION_METHOD = 'basic'
PRIVATE_MEDIA_ROOT = ''

# Django-Registration
ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_REDIRECT_URL = '/admin/'
USERS_REGISTRATION_MODE = 'OPEN' # [OPEN|RESTRICTED|CLOSED]
EMAIL_REGISTRATION_APPROVE = '' # Only required if USERS_REGISTRATION_MODE = RESTRICTED

# rest_framework
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
#        'controller.apps.api.filters.JSONPointerFilterBackend',
        'rest_framework.filters.DjangoFilterBackend',),
    'DEFAULT_PERMISSION_CLASSES': (
        'permissions.api.TestbedPermissionBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
#    'PAGINATE_BY': 10,
#    'PAGINATE_BY_PARAM': 'page_size',
}

USE_ETAGS = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/dev/null',
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'state.models': {
#            'handlers': ['console', 'logfile'],
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}



###################################
## CONTROLLER APPS CONFIGURATION ##
###################################

# common.api
CUSTOM_API_ROOT = 'controller.api.Base'

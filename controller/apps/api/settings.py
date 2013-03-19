from django.conf import settings

ugettext = lambda s: s


API_REL_BASE_URL = getattr(settings, 'API_REL_BASE_URL', 'http://confine-project.eu/rel/server/')



from django.conf import settings

ugettext = lambda s: s

# Cache node_db every 1200 seconds
COMMUNITYNETWORKS_CACHE_NODE_DB_SCHEDULE = getattr(settings, 'COMMUNITYNETWORKS_CACHE_NODE_DB_SCHEDULE', 1200)

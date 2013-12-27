from StringIO import StringIO

from django.core.management import call_command
from django.db import transaction


def sync_plugins_action(name):
    @transaction.atomic
    def sync_plugins(modeladmin, request, queryset):
        content = StringIO()
        call_command('sync%s' % name, stdout=content)
        content.seek(0)
        found = [ line.split(' ')[1] for line in content.read().splitlines() ]
        msg = '%i %s have been found (%s).' % (len(found), name, ', '.join(found))
        modeladmin.message_user(request, msg)
    sync_plugins.description = "Syncronize existing %s with the database." % name
    sync_plugins.url_name = 'sync-plugins'
    sync_plugins.verbose_name = 'Sync plugins'
    return sync_plugins

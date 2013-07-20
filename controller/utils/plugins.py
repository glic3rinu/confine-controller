from StringIO import StringIO

from django.core.management import call_command
from django.db import models, transaction


class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)


class PluginModelQuerySet(models.Manager):
    def active(self, **kwargs):
        return self.filter(is_active=True, **kwargs)


class PluginModel(models.Model):
    is_active = models.BooleanField(default=False)
    label = models.CharField(max_length=128, blank=True, unique=True)
    module = models.CharField(max_length=256, blank=True)
    
    objects = PluginModelQuerySet()
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return self.label
    
    @property
    def instance(self):
        if not hasattr(self, '_instance'):
            module = __import__(self.module, fromlist=[self.label])
            plugin_class = getattr(module, self.label)
            self._instance = plugin_class()
        return self._instance
    
    @property
    def description(self):
        return self.instance.description


def sync_plugins_action(name):
    @transaction.commit_on_success
    def sync_plugins(modeladmin, request, queryset):
        content = StringIO()
        call_command('sync%s' % name, stdout=content)
        content.seek(0)
        found = [ line.split(' ')[1] for line in content.read().splitlines() ]
        msg = '%i %s had been found (%s)' % (len(found), name, ', '.join(found))
        modeladmin.message_user(request, msg)
    sync_plugins.description = "Syncronize existing %s with the database" % name
    sync_plugins.url_name = 'sync-plugins'
    sync_plugins.verbose_name = 'sync plugins'
    return sync_plugins

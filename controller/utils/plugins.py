from django.db import models


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


class PluginModelQuerySet(models.query.QuerySet):
    def active(self, **kwargs):
        return self.filter(is_active=True, **kwargs)


class PluginModel(models.Model):
    is_active = models.BooleanField(default=False)
    label = models.CharField(max_length=128, blank=True, unique=True)
    module = models.CharField(max_length=256, blank=True)
    
    objects = PluginModelQuerySet
    
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

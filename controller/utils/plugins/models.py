from django.db import models


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

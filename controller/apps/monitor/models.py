from django.db import models
from django.utils import timezone
from jsonfield import JSONField


from . import settings


class TimeSerie(models.Model):
    name = models.CharField(max_length=64)
    value = JSONField()
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        index_together = [['name', 'date']]
        get_latest_by = 'date'
    
    @property
    def has_expired(self):
        now = timezone.now()
        return (now-self.date).total_seconds() > settings.MONITOR_EXPIRE_SECONDS
    
    @property
    def values(self):
        return self.value
    
    @classmethod
    def get_monitors(cls):
        return monitors
    
    @classmethod
    def get_monitor(cls, name):
        for monitor in monitors:
            if monitor.name == name:
                return monitor
        raise KeyError("Monitor with name %s not found" % name)
    
    @property
    def monitor(self):
        return type(self).get_monitor(self.name)
    
    def apply_relativity(self, previous):
        self.monitor.apply_relativity(self, previous)


# Register monitor singletons
monitors = []
for monitor in settings.MONITOR_MONITORS:
    kwargs = {}
    if len(monitor) is 2:
        kwargs = monitor[1]
    monitor = monitor[0]
    module = '.'.join(monitor.split('.')[:-1])
    cls_name = monitor.split('.')[-1]
    monitor_cls = getattr(__import__(module, fromlist=[cls_name]), cls_name)
    monitors.append(monitor_cls(**kwargs))

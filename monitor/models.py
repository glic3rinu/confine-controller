from django.contrib.contenttypes import generic
from django.db import models
#from djcelery.models import IntervalSchedule, CrontabSchedule)


#class Metric(models.Model):
#    name = models.CharFiel()
#    interval = models.ForeignKey(IntervalSchedule, null=True, blank=True)
#    crontab = models.ForeignKey(CrontabSchedule, null=True, blank=True,
#                                help_text="Use one of interval/crontab")
#    args = models.TextField("Arguments", blank=True, default="[]",
#                            help_text="JSON encoded positional arguments")
#    kwargs = models.TextField("Keyword arguments", blank=True, default="{}",
#                              help_text="JSON encoded keyword arguments")
#    is_active = models.BooleanField(default=True)
#    last_run_at = models.DateTimeField(auto_now=False, auto_now_add=False,
#                                       editable=False, blank=True, null=True)
#    total_run_count = models.PositiveIntegerField(default=0, editable=False)
#    date_changed = models.DateTimeField(auto_now=True)
#    description = models.TextField(blank=True)



class TimeSerie(models.Model):
    content_type = models.ForeignKey(generic.ContentType)
    object_id = models.PositiveIntegerField()
#    metric = models.ForeignKey(Metric)
    time = models.DateTimeField(auto_now_add=True)
    data = models.CharField(max_length=128, null=True)
    metadata = models.CharField(max_length=256)
    
    content_object = generic.GenericForeignKey()
    
    def __unicode__(self):
        return str(self.content_object)
    
    @classmethod
    def store_glet(cls, obj, glet, get_data=lambda g: g.value):
        data = get_data(glet)
        metadata = {'exception': glet._exception}
        cls.objects.create(content_object=obj, metadata=metadata, data=data)


class Interpreter(object):
    pass
    
#class Policy(models.Model):
#    metric = 
#    interval = 
#    action =

#    # TODO Execute action through paramiko

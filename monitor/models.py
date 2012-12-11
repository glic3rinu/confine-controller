from django.contrib.contenttypes import generic
from django.db import models
from djcelery.models import INtervalSchedule, CrontabSchedule)


class Metric(models.Model):
    name = models.CharFiel()
    interval = models.ForeignKey(IntervalSchedule, null=True, blank=True)
    crontab = models.ForeignKey(CrontabSchedule, null=True, blank=True,
                                help_text="Use one of interval/crontab")
    args = models.TextField("Arguments", blank=True, default="[]",
                            help_text="JSON encoded positional arguments")
    kwargs = models.TextField("Keyword arguments", blank=True, default="{}",
                              help_text="JSON encoded keyword arguments")
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(auto_now=False, auto_now_add=False,
                                       editable=False, blank=True, null=True)
    total_run_count = models.PositiveIntegerField(default=0, editable=False)
    date_changed = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)



class TimeSeriesData(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    metric = models.ForeignKey(Metric)
    time = models.DateTimeField(auto_add=True)
    value = models.CharField(max_length=128)
    
    content_object = generic.GenericForeignKey()


class Policy(models.Model):
    metric = 
    interval = 
    action =

    # TODO Execute action through paramiko

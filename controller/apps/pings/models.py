from __future__ import absolute_import

from time import time

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from controller.utils.apps import is_installed
from controller.utils.time import heartbeat_expires

from .settings import PING_DEFAULT_INSTANCE, PING_INSTANCES, PING_COUNT


for instance in PING_INSTANCES:
    # This has to be before Ping class in order to avoid import problems
    if is_installed(instance.get('app')):
        context = {
            'app': instance.get('app'),
            'model': instance.get('model').split('.')[1] }
        exec('from %(app)s.models import %(model)s as model' % context)
        model.add_to_class('pings', generic.GenericRelation('pings.Ping'))


class Ping(models.Model):
    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'
    NODATA = 'NODATA'
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    samples = models.PositiveIntegerField(default=PING_COUNT)
    packet_loss = models.PositiveIntegerField(null=True)
    min = models.DecimalField('RTT min', decimal_places=3, max_digits=9, null=True)
    avg = models.DecimalField('RTT avg', decimal_places=3, max_digits=9, null=True)
    max = models.DecimalField('RTT max', decimal_places=3, max_digits=9, null=True)
    mdev = models.DecimalField('RTT mdev', decimal_places=3, max_digits=9, null=True)
    date = models.DateTimeField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        index_together = [['object_id', 'content_type', 'date']]
        get_latest_by = 'date'
    
    @classmethod
    def get_state(cls, obj):
        try:
            last = obj.pings.all().latest()
        except Ping.DoesNotExist:
            return cls.NODATA
        settings = cls.get_instance_settings(obj)
        kwargs = {
            'freq': settings.get('schedule'),
            'expire_window': settings.get('expire_window')}
        if time() > heartbeat_expires(last.date, **kwargs):
            return cls.NODATA
        if last.packet_loss == 100:
            return cls.OFFLINE
        return cls.ONLINE
    
    @classmethod
    def get_instance_settings(cls, model, setting=None):
        if not (isinstance(model, unicode) or isinstance(model, str)):
            model = "%s.%s" % (model._meta.app_label, model._meta.object_name)
        for instance in PING_INSTANCES:
            settings = PING_DEFAULT_INSTANCE.copy()
            settings.update(instance)
            if model == settings.get('model'):
                if setting:
                    return settings.get(setting)
                return settings


# workaround django issue #22594 and controller #448
# https://code.djangoproject.com/ticket/22594
# http://redmine.confine-project.eu/issues/448
from django.db.models.signals import pre_delete
from django.dispatch import receiver

@receiver(pre_delete)
def pre_delete_receiver(sender, instance,**kwargs):
    pings = getattr(instance, 'pings', False)
    if pings:
        pings.all().delete()

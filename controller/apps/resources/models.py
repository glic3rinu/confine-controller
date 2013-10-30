from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import lazy

from controller.utils import autodiscover

from . import ResourcePlugin


autodiscover('resources')


class BaseResource(models.Model):
    name = models.CharField(max_length=128,
            # TODO based on providers and consumers
            choices=[ (r.name, r.name) for r in ResourcePlugin.plugins ])
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        abstract = True
        unique_together = ['name', 'object_id', 'content_type']
    
    def __unicode__(self):
        return self.name
    
    @property
    def unit(self):
        try:
            return self.instance.unit
        except KeyError:
            return ''
    
    @property
    def instance(self):
        for instance in ResourcePlugin.plugins:
            if instance.name == self.name:
                return instance
        raise KeyError('Resource "%s" not registered' % self.name)


class Resource(BaseResource):
    max_sliver = models.PositiveIntegerField(null=True, blank=True)
    dflt_sliver = models.PositiveIntegerField()


class ResourceReq(BaseResource):
    req = models.PositiveIntegerField(null=True, blank=True)

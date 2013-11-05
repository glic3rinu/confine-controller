from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import lazy

from controller.utils import autodiscover

from . import ResourcePlugin


autodiscover('resources')


class BaseResource(models.Model):
    name = models.CharField(max_length=128)
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
    
    # TODO validate names depending on content_type!


class Resource(BaseResource):
    max_sliver = models.PositiveIntegerField(null=True, blank=True)
    dflt_sliver = models.PositiveIntegerField("Default sliver")


class ResourceReq(BaseResource):
    req = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Resource request"
        verbose_name_plural = "Resource requests"


for producer_model in ResourcePlugin.get_producers_models():
    producer_model.add_to_class('resources', generic.GenericRelation('resources.Resource'))

for consumer_model in ResourcePlugin.get_consumers_models():
    consumer_model.add_to_class('resources', generic.GenericRelation('resources.ResourceReq'))

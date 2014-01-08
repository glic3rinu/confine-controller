from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import lazy

from controller.utils import autodiscover
from controller.utils.functional import cached

from . import ResourcePlugin


class BaseResource(models.Model):
    PRODUCER = 'producer'
    CONSUMER = 'consumer'
    
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
        return self.instance.unit if self.name else ''
    
    @property
    @cached
    def instance(self):
        return ResourcePlugin.get(self.name)
    
    def clean(self):
        """ Make sure self.name is a valid resource """
        super(BaseResource, self).clean()
        try:
            instance = self.instance
        except KeyError as e:
            raise ValidationError(str(e))
        # FIXME self.content_type is not available during form.full_clean()
#        category = self.PRODUCER if type(self) is Resource else self.CONSUMER
#        opts = self.content_type.model_class()._meta
#        label = '%s.%s' % (opts.app_label, opts.object_name)
#        if not label in getattr(instance, category+'s'):
#            msg = "%s is not a resource %s of %s" % (label, category, instance.name)
#            raise ValidationError(msg)


class Resource(BaseResource):
    max_sliver = models.PositiveIntegerField(null=True, blank=True)
    dflt_sliver = models.PositiveIntegerField("Default sliver")
    
    def clean(self):
        super(Resource, self).clean()
        self.instance.clean(self)


# TODO rename name to res_name
class ResourceReq(BaseResource):
    req = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Resource request"
        verbose_name_plural = "Resource requests"
    
    def clean(self):
        super(ResourceReq, self).clean()
        self.instance.clean_req(self)


autodiscover('resources')

for producer_model in ResourcePlugin.get_producers_models():
    producer_model.add_to_class('resources', generic.GenericRelation('resources.Resource'))

for consumer_model in ResourcePlugin.get_consumers_models():
    consumer_model.add_to_class('resources', generic.GenericRelation('resources.ResourceReq'))

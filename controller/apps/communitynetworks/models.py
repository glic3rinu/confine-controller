from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from controller.models.fields import URIField
from controller.utils import is_installed
from nodes.models import Node, Server

from .tasks import cache_node_db


# Hook Community Network support for related models
# This must be at the begining in order to avoid wired import problems
related_models = [Node, Server]
if is_installed('mgmtnetworks.tinc'):
    from mgmtnetworks.tinc.models import Gateway
    related_models.append(Gateway)


class CnHost(models.Model):
    """
    Describes a host in the Community Network.
    """
    app_url = models.URLField('Community network URL', blank=True,
        help_text='Optional URL pointing to a description of this host/device '
                  'in its CN\'s node DB web application.')
    cndb_uri = URIField('Community network database URI', blank=True,
        help_text='Optional URI for this host/device in its CN\'s CNDB REST API')
    cndb_cached_on = models.DateTimeField('CNDB cached on', null=True, blank=True,
        help_text='Last date that CNDB information for this host/device was '
                  'successfully retrieved.')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return str(self.pk)
    
    def save(self, *args, **kwargs):
        """ Setting cndb_uri resets cndb_cached_on to null. """
        if self.pk:
            db_host = CnHost.objects.get(pk=self.pk)
            if self.cndb_uri != db_host.cndb_uri:
                self.cndb_cached_on = None
        super(CnHost, self).save(*args, **kwargs)
    
    def cache_node_db(self, async=False):
        if async:
            defer(cache_node_db.delay, self)
        else:
            cache_node_db(self)


# Hook Community Network support for related models
for model in related_models:
    model.add_to_class('cn', generic.GenericRelation('communitynetworks.CnHost'))

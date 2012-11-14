from django.conf import settings as project_settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from nodes.models import Node, Server
from .tasks import cache_node_db

class CnHost(models.Model):
    """
    Describes a host in the Community Network.
    """
    app_url = models.URLField('Community Network URL', blank=True,
        help_text='Optional URL pointing to a description of this host/device '
                  'in its CN\'s node DB web application.')
    # TODO create URIField
    cndb_uri = models.URLField('Community Network Database URI', blank=True,
        help_text='Optional URI for this host/device in its CN\'s CNDB REST API')
    cndb_cached_on = models.DateTimeField('CNDB cached on', null=True, blank=True,
        help_text='Last date that CNDB information for this host/device was '
                  'successfully retrieved.')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(max_length=36)
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return str(self.pk)
    
    def save(self, *args, **kwargs):
        """ Setting cndb_uri resets cndb_cached_on to null. """
        if self.pk:
            db_host = type(self).objects.get(pk=self.pk)
            if self.cndb_uri != db_host.cndb_uri:
                self.cndb_cached_on = None
        super(CnHost, self).save(*args, **kwargs)
    
    def cache_node_db(self, async=False):
        if async: defer(cache_node_db.delay, self)
        else: cache_node_db(self)


# Hook Community Network support for related models
related_models = [Node, Server]
if 'tinc' in project_settings.INSTALLED_APPS:
    from tinc.models import Gateway
    related_models.append(Gateway)

@property
def cn(self):
    try: return self.related_cnhost.get()
    except CnHost.DoesNotExist: return {}

for model in related_models:
    related_cnhost = generic.GenericRelation('community_network.CnHost')
    related_cnhost.contribute_to_class(model, 'related_cnhost')
    model.cn = cn

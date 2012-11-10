from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import models
from nodes.models import CnHost, Server, Node
from tinc import settings
import re


class Host(models.Model):
    """
    Describes an odd host computer connected to the testbed (through the 
    management network) with a known administrator.
    """
    description = models.CharField(max_length=256, 
        help_text='Free-form textual description of this host.')
    admin = models.ForeignKey(User, 
        help_text='The user who administrates this host (its creator by default)')

    def __unicode__(self):
        return self.description


class TincHost(models.Model):
    """
    Base class that describes the basic attributs of a Tinc Host. 
    A Tinc Host could be a Server or a Client.
    """
    pubkey = models.TextField(unique=True, verbose_name='Public Key',
        help_text='PEM-encoded RSA public key used on tinc management network.')
    connect_to = models.ManyToManyField('tinc.TincAddress', blank=True,
        help_text='A list of tinc addresses this host connects to.')
    
    class Meta:
        abstract = True
    
    @property
    def name(self):
        return str(self)


class Gateway(CnHost):
    """
    Describes a Gateway in the testbed. A machine giving entry to the testbed's 
    management network from a set of network islands. It can help connect 
    different parts of a management network located at different islands over 
    some link external to them (e.g. the Internet).
    """
    related_tincserver = generic.GenericRelation('tinc.TincServer')
    
    @property
    def tinc(self):
        try: return self.related_tincserver.get()
        except TincServer.DoesNotExist: return {}


class TincServer(TincHost):
    """
    Describes a Tinc Server in the testbed. A Tinc Server can be a Gateway or 
    the testbed server itself.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(max_length=36)
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')

    def __unicode__(self):
        if self.content_type.model == 'server': return 'server'
        return "%s_%s" % (self.content_type.model, self.object_id)

    @property
    def addresses(self):
        return self.tincaddress_set.all()


class Island(models.Model):
    """
    Describes a network island (i.e. a disconnected part of a community network)
    where the testbed is reachable from. A testbed is reachable from an island
    when there is a gateway that gives access to the testbed server (possibly
    through other gateways), or when the server itself is in that island.
    """
    name = models.CharField(max_length=32, unique=True, 
        help_text='The unique name of this island. A single line of free-form '
                  'text with no whitespace surrounding it.',
        validators=[validators.RegexValidator(re.compile('^[a-z][_0-9a-z]*[0-9a-z]$.'), 
                   'Enter a valid name.', 'invalid')])
    description = models.TextField(blank=True, 
        help_text='Optional free-form textual description of this island.')
    
    def __unicode__(self):
        return self.name


class TincAddress(models.Model):
    """
    Describes an IP Address of a Tinc Server.
    """
    ip_addr = models.GenericIPAddressField(protocol='IPv6', 
        help_text='IPv6 address of this tinc address.',
        verbose_name='IP Address')
    port = models.SmallIntegerField(default=settings.TINC_DEFAULT_PORT, 
        help_text='TCP/UDP port of this tinc address.')
    island = models.ForeignKey(Island,
        help_text='<a href="http://wiki.confine-project.eu/arch:rest-api#island_'
                  'at_server">Island</a> this tinc address is reachable from.')
    server = models.ForeignKey(TincServer)
    
    class Meta:
        verbose_name_plural = 'Tinc Addresses'
    
    def __unicode__(self):
        return str(self.ip_addr)
    
    @property
    def name(self):
        return self.server.name
    
    @property
    def pubkey(self):
        return self.server.pubkey


class TincClient(TincHost):
    """
    Describes a Tinc Client in the testbed. A tinc client can be a testbed node
    or a host.
    """
    island = models.ForeignKey(Island, help_text='Island this client reaches to.')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(max_length=36)
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return "%s_%s" % (self.content_type.model, self.object_id)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            super(TincClient, self).save(*args, **kwargs)
            self.connect_to = self.island.tincaddress_set.all()
        else:
            super(TincClient, self).save(*args, **kwargs)
    
    def set_island(self):
        self.connect_to = self.island.tincaddress_set.all()
        self.save()


# Monkey-Patching Section

# Hook TincClient support for related models
related_models = [Host, Node]

@property
def tinc(self):
    try: return self.related_tincclient.get()
    except TincClient.DoesNotExist: return {}

for model in related_models:
    related_tincclient = generic.GenericRelation('tinc.TincClient')
    related_tincclient.contribute_to_class(model, 'related_tincclient')
    model.tinc = tinc

# Hook TincServer support to Server
@property
def tinc(self):
    try: return self.related_tincserver.get()
    except TincServer.DoesNotExist: return {}

related_tincserver = generic.GenericRelation('tinc.TincServer')
related_tincserver.contribute_to_class(Server, 'related_tincserver')
Server.tinc = tinc


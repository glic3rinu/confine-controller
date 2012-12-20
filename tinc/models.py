import re

# TODO: migrate to M2Crypto
import M2Crypto
from django.contrib.auth import get_user_model
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import models
from django_transaction_signals import defer
from IPy import IP

from common.ip import split_len, int_to_hex_str
from common.validators import validate_host_name, OrValidator, validate_rsa_pubkey
from nodes.models import Server, Node


from . import settings
from .settings import MGMT_IPV6_PREFIX
from .tasks import update_tincd


class Host(models.Model):
    """
    Describes an odd host computer connected to the testbed (through the 
    management network) with a known administrator.
    """
    description = models.CharField(max_length=256, 
        help_text='Free-form textual description of this host.')
    owner = models.ForeignKey(get_user_model(), 
        help_text='The user who administrates this host (its creator by default)')
    
    def __unicode__(self):
        return self.description


class TincHost(models.Model):
    """
    Base class that describes the basic attributs of a Tinc Host. 
    A Tinc Host could be a Server or a Client.
    """
    pubkey = models.TextField('Public Key', unique=True, null=True, blank=True, 
        help_text='PEM-encoded RSA public key used on tinc management network.',
        validators=[validate_rsa_pubkey])
    connect_to = models.ManyToManyField('tinc.TincAddress', blank=True,
        help_text='A list of tinc addresses this host connects to.')
    
    class Meta:
        abstract = True
    
    @property
    def name(self):
        return str(self)
    
    def clean(self):
        """ Empty pubkey as NULL instead of empty string """
        if self.pubkey == '':
            self.pubkey = None
        super(TincHost, self).clean()
    
    def get_tinc_up(self):
        """ tinc-up file content """
        ip = "%s/%s" % (self.address, MGMT_IPV6_PREFIX.split('/')[1])
        return '#!/bin/sh\nip -6 link set "$INTERFACE" up mtu 1400\nip -6 addr add %s dev "$INTERFACE"\n' % ip
    
    def get_tinc_down(self):
        """ tinc-down file content """
        ip = "%s/%s" % (self.address, MGMT_IPV6_PREFIX.split('/')[1])
        return '#!/bin/sh\nip -6 addr del %s dev "$INTERFACE"\nip -6 link set "$INTERFACE" down\n' % ip


class Gateway(models.Model):
    """
    Describes a Gateway in the testbed. A machine giving entry to the testbed's 
    management network from a set of network islands. It can help connect 
    different parts of a management network located at different islands over 
    some link external to them (e.g. the Internet).
    """
    related_tincserver = generic.GenericRelation('tinc.TincServer')
    description = models.CharField(max_length=256,
        help_text='Free-form textual description of this gateway.')
    
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
    object_id = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        if self.content_type.model == 'server': return 'server'
        return "%s_%s" % (self.content_type.model, self.object_id)
    
    @property
    def addresses(self):
        return self.tincaddress_set.all()
    
    @property
    def address(self):
        """ IPV6 management address """
        ipv6_words = MGMT_IPV6_PREFIX.split(':')[:3]
        if self.content_type.model == 'server':
            # MGMT_IPV6_PREFIX:0:0000::2/128
            return IP(':'.join(ipv6_words) + '::2')
        elif self.content_type.model == 'gateway':
            # MGMT_IPV6_PREFIX:0:0001:gggg:gggg:gggg/128
            ipv6_words.extend(['0', '0001'])
            ipv6_words.extend(split_len(int_to_hex_str(self.object_id, 12), 4))
            return IP(':'.join(ipv6_words))
    
    @property
    def subnet(self):
        return self.address
    
    def get_host(self):
        # FIXME this depends on each node(node.tinc.island)
        #       maybe an optional node/tincclient argument and introspect islands?
        host = ""
        for addr in self.addresses:
            host += "Address = %s\n" % addr.addr
        host += "Port = 655\n"
        host += "Subnet = %s\n\n" % self.subnet.strNormal()
        host += "%s\n" % self.pubkey
        return host


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
        validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'), 
                   'Enter a valid name.', 'invalid')])
    description = models.TextField(blank=True, 
        help_text='Optional free-form textual description of this island.')
    
    def __unicode__(self):
        return self.name


class TincAddress(models.Model):
    """
    Describes an IP Address of a Tinc Server.
    """
    addr = models.CharField('Address', max_length=128,
        help_text='The tinc IP address or host name of the host this one connects to.',
        validators=[OrValidator([validators.validate_ipv4_address, validate_host_name])])
    port = models.SmallIntegerField(default=settings.TINC_DEFAULT_PORT, 
        help_text='TCP/UDP port of this tinc address.')
    island = models.ForeignKey(Island,
        help_text='<a href="http://wiki.confine-project.eu/arch:rest-api#island_'
                  'at_server">Island</a> this tinc address is reachable from.')
    server = models.ForeignKey(TincServer)
    
    class Meta:
        verbose_name_plural = 'Tinc Addresses'
    
    def __unicode__(self):
        return str(self.addr)
    
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
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return "%s_%s" % (self.content_type.model, self.object_id)
    
    def save(self, *args, **kwargs):
        # FIXME bug in django, this is a workaround
        # https://code.djangoproject.com/ticket/19467
        if self.pubkey == '': self.pubkey = None
        # end of workaround
        if not self.pk:
            super(TincClient, self).save(*args, **kwargs)
            self.set_island()
        else:
            super(TincClient, self).save(*args, **kwargs)
        self.update_tincd()
    
    def delete(self, *args, **kwargs):
        super(TincClient, self).delete(*args, **kwargs)
        self.update_tincd()
    
    def set_island(self):
        self.connect_to = self.island.tincaddress_set.all()
        self.save()
    
    @property
    def address(self):
        """ IPV6 management address """
        ipv6_words = MGMT_IPV6_PREFIX.split(':')[:3]
        if self.content_type.model == 'node':
            # MGMT_IPV6_PREFIX:N:0000::2/64 i
            ipv6_words.append(int_to_hex_str(self.object_id, 4))
            return IP(':'.join(ipv6_words) + '::2')
        elif self.content_type.model == 'host':
            # MGMT_IPV6_PREFIX:0:2000:hhhh:hhhh:hhhh/128
            ipv6_words.extend(['0', '2000'])
            ipv6_words.extend(split_len(int_to_hex_str(self.object_id, 12), 4))
            return IP(':'.join(ipv6_words))
    
    @property
    def subnet(self):
        if self.content_type.model == 'node':
            return self.address.make_net(64)
        elif self.content_type.model == 'host':
            return self.address
    
    def update_tincd(self, async=True):
        if async:
            defer(update_tincd.delay)
        else:
            update_tincd()
    
    def get_host(self):
        """ returns tincd hosts file content """
        return "Subnet = %s\n\n%s" % (self.subnet.strNormal(), self.pubkey)
    
    def get_config(self):
        """ returns client tinc.conf file content """
        config = "Name = %s\n" % self.name
        for server in self.connect_to.all():
            config += "ConnectTo = %s\n" % server.name
        return config
    
    def generate_key(self, commit=False):
        # TODO move to ssl.py ?
        key = M2Crypto.RSA.gen_key(2048, 65537)
        mem = M2Crypto.BIO.MemoryBuffer()
        key.save_key_bio(mem, cipher=None)
        private = mem.getvalue()
        if commit:
            key.save_pub_key_bio(mem)
            self.pubkey = mem.getvalue()
            self.save()
        return private
    
    class UpdateTincdError(Exception): pass


# Monkey-Patching Section

# Hook TincClient support for related models
related_models = [Host, Node]

@property
def tinc(self):
    return self.related_tincclient.get()

for model in related_models:
    model.add_to_class('related_tincclient', generic.GenericRelation('tinc.TincClient'))
    model.add_to_class('tinc', tinc)

# Hook TincServer support to Server
@property
def tinc(self):
    return self.related_tincserver.get()

Server.add_to_class('related_tincserver', generic.GenericRelation('tinc.TincServer'))
Server.add_to_class('tinc', tinc)


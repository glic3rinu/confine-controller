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
    related_tincclient = generic.GenericRelation('tinc.TincClient')
    
    def __unicode__(self):
        return self.description
    
    @property
    def tinc(self):
        ct = ContentType.objects.get_for_model(self)
        obj, created = TincClient.objects.get_or_create(object_id=self.pk, content_type=ct)
        return obj
    
    @property
    def mgmt_addr(self):
        return self.tinc.address


class TincHost(models.Model):
    """
    Base class that describes the basic attributs of a Tinc Host.
    A Tinc Host could be a Server or a Client.
    """
    pubkey = models.TextField('Public Key', unique=True, null=True, blank=True,
        help_text='PEM-encoded RSA public key used on tinc management network.',
        validators=[validate_rsa_pubkey])
    
    class Meta:
        abstract = True
    
    @property
    def name(self):
        return str(self)
    
    def clean(self):
        """ Empty pubkey as NULL instead of empty string """
        # TODO  There is a bug in django, when the object is created on inlines
        #       model.clean() doesn't get called. When saving chanegs it is called
        #       A more elaborated describtion is required for this tiket:
        #       https://code.djangoproject.com/ticket/19467
        if self.pubkey == '':
            self.pubkey = None
        else:
            self.pubkey = self.pubkey.strip()
        super(TincHost, self).clean()
    
    def get_tinc_up(self):
        """ Returns tinc-up file content """
        ip = "%s/%s" % (self.address, settings.TINC_MGMT_IPV6_PREFIX.split('/')[1])
        return ('#!/bin/sh\n'
                'ip -6 link set "$INTERFACE" up mtu 1400\n'
                'ip -6 addr add %s dev "$INTERFACE"\n' % ip)
    
    def get_tinc_down(self):
        """ Returns tinc-down file content """
        ip = "%s/%s" % (self.address, settings.TINC_MGMT_IPV6_PREFIX.split('/')[1])
        return ('#!/bin/sh\n'
                'ip -6 addr del %s dev "$INTERFACE"\n'
                'ip -6 link set "$INTERFACE" down\n' % ip)


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
        ct = ContentType.objects.get_for_model(self)
        obj, created = TincServer.objects.get_or_create(object_id=self.pk, content_type=ct)
        return obj
    
    @property
    def mgmt_addr(self):
        return self.tinc.address


class TincServer(TincHost):
    """
    Describes a Tinc Server in the testbed. A Tinc Server can be a Gateway or 
    the testbed server itself.
    """
    is_active = models.BooleanField(default=True, 
        help_text="Whether this tinc server is active. It should only be made "
                  "false if there are other tinc servers with addresses in the "
                  "same islands of the addresses provided by this server.")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        if self.content_type.model == 'server': return 'server'
        return "%s_%s" % (self.content_type.model, self.object_id)
    
    def clean(self):
        # TODO prevent changes when is_active = true, but take into account that 
        #       change is_active to true is also a change, so this can be  a bit triky.
#        if self.is_active:
#            raise ValidationError("Changes on tinc servers are not allowed when is active.")
        super(TincServer, self).clean()
    
    @property
    def addresses(self):
        return self.tincaddress_set.all()
    
    @property
    def address(self):
        """ IPV6 management address """
        ipv6_words = settings.TINC_MGMT_IPV6_PREFIX.split(':')[:3]
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
        """ Returns tincd host file """
        # TODO order by island
        host = ""
        for addr in self.addresses:
            host += "Address = %s %d\n" % (addr.addr, addr.port)
        host += "Subnet = %s\n\n" % self.subnet.strNormal()
        if self.pubkey:
            host += "%s" % self.pubkey
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
        validators=[validators.RegexValidator('^[\w.@+-]+$',
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
    port = models.SmallIntegerField(default=settings.TINC_PORT_DFLT, 
        help_text='TCP/UDP port of this tinc address.')
    island = models.ForeignKey(Island, null=True, blank=True,
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


class TincClient(TincHost):
    """
    Describes a Tinc Client in the testbed. A tinc client can be a testbed node
    or a host.
    """
    island = models.ForeignKey(Island, null=True, blank=True,
        help_text='An optional island used to hint where this tinc client reaches to.')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return "%s_%s" % (self.content_type.model, self.object_id)
    
    def save(self, *args, **kwargs):
        super(TincClient, self).save(*args, **kwargs)
        self.update_tincd(async=True)
    
    def delete(self, *args, **kwargs):
        super(TincClient, self).delete(*args, **kwargs)
        self.update_tincd(async=True)
    
    @property
    def address(self):
        """ Calculates IPV6 management address """
        ipv6_words = settings.TINC_MGMT_IPV6_PREFIX.split(':')[:3]
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
    
    @property
    def connect_to(self):
        """ Returns all active TincServers to use on tincd ConnectTo """
        return TincServer.objects.filter(is_active=True)
    
    def update_tincd(self, async=True):
        """ Update local tinc daemon configuration """
        if async:
            defer(update_tincd.delay)
        else:
            update_tincd()
    
    def get_host(self):
        """ Returns tincd hosts file content """
        host = "Subnet = %s" % self.subnet.strNormal()
        if self.pubkey:
            host += "\n\n%s" % self.pubkey
        return host
    
    def get_config(self):
        """ Returns client tinc.conf file content """
        config = ["Name = %s" % self.name]
        # TODO Order by island
        # TODO order by some priority?
        for server in self.connect_to.all():
            config.append("ConnectTo = %s" % server.name)
        return '\n'.join(config)
    
    def generate_key(self, commit=False):
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

# Hook TincClient support to Node
@property
def tinc(self):
    ct = ContentType.objects.get_for_model(self)
    obj, created = TincClient.objects.get_or_create(object_id=self.pk, content_type=ct)
    return obj

Node.add_to_class('related_tincclient', generic.GenericRelation('tinc.TincClient'))
Node.add_to_class('tinc', tinc)

# Hook TincServer support to Server
@property
def tinc(self):
    ct = ContentType.objects.get_for_model(self)
    obj, created = TincServer.objects.get_or_create(object_id=self.pk, content_type=ct)
    return obj

Server.add_to_class('related_tincserver', generic.GenericRelation('tinc.TincServer'))
Server.add_to_class('tinc', tinc)

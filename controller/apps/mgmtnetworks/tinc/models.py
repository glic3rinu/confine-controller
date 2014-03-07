from django.contrib.auth import get_user_model
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import models
from django_transaction_signals import defer
from IPy import IP

from controller import settings as controller_settings
from controller.models.fields import RSAPublicKeyField
from controller.models.utils import generate_chainer_manager
from controller.utils.ip import split_len, int_to_hex_str
from controller.core.validators import validate_host_name, validate_name, OrValidator
from nodes.models import Server, Node
from pki import Bob

from . import settings, backend
from .tasks import update_tincd


class Host(models.Model):
    """
    Describes an odd host computer connected to the testbed (through the 
    management network) with a known administrator.
    """
    description = models.CharField(max_length=256,
            help_text='Free-form textual description of this host.')
    owner = models.ForeignKey(get_user_model(), related_name='tinc_hosts',
            help_text='The user who administrates this host (its creator by default)')
    island = models.ForeignKey('nodes.Island', null=True, blank=True,
            help_text='An optional island used to hint where this tinc client reaches to.')
    related_tincclient = generic.GenericRelation('tinc.TincClient')
    
    def __unicode__(self):
        return self.description
    
    @property
    def tinc(self):
        ct = ContentType.objects.get_for_model(self)
        obj, __ = TincClient.objects.get_or_create(object_id=self.pk, content_type=ct)
        return obj
    
    @property
    def mgmt_net(self):
        return backend(self)


class TincHost(models.Model):
    """
    Base class that describes the basic attributs of a Tinc Host.
    A Tinc Host could be a Server or a Client.
    """
    pubkey = RSAPublicKeyField('public Key', blank=True, null=True, unique=True,
            help_text='PEM-encoded RSA public key used on tinc management network.')
    
    class Meta:
        abstract = True
    
    @property
    def name(self):
        return str(self)
    
    def save(self, *args, **kwargs):
        super(TincHost, self).save(*args, **kwargs)
        defer(update_tincd.delay)
    
    def delete(self, *args, **kwargs):
        super(TincHost, self).delete(*args, **kwargs)
        defer(update_tincd.delay)
    
    def get_tinc_up(self):
        """ Returns tinc-up file content """
        ip = "%s/%s" % (self.address, controller_settings.MGMT_IPV6_PREFIX.split('/')[1])
        return ('#!/bin/sh\n'
                'ip -6 link set "$INTERFACE" up mtu 1400\n'
                'ip -6 addr add %s dev "$INTERFACE"\n' % ip)
    
    def get_tinc_down(self):
        """ Returns tinc-down file content """
        ip = "%s/%s" % (self.address, controller_settings.MGMT_IPV6_PREFIX.split('/')[1])
        return ('#!/bin/sh\n'
                'ip -6 addr del %s dev "$INTERFACE"\n'
                'ip -6 link set "$INTERFACE" down\n' % ip)
    
    @property
    def address(self):
        raise NotImplementedError('Child classes must implement this method')


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
        obj, __ = TincServer.objects.get_or_create(object_id=self.pk, content_type=ct)
        return obj
    
    def mgmt_net(self):
        return backend(self)


class TincServerQuerySet(models.query.QuerySet):
    def gateways(self, *args, **kwargs):
        server_ct = ContentType.objects.get_for_model(Server)
        return self.exclude(content_type=server_ct).filter(*args, **kwargs)


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
    objects = generate_chainer_manager(TincServerQuerySet)
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        if self.content_type.model == 'server':
            return 'server'
        return u'%s_%s' % (self.content_type.model, self.object_id)
    
    def clean(self):
        # TODO prevent changes when is_active = true, but take into account that 
        #       change is_active to true is also a change, so this can be  a bit triky.
#        if self.is_active:
#            raise ValidationError("Changes on tinc servers are not allowed when is active.")
        super(TincServer, self).clean()
    
    @property
    def address(self):
        """ IPV6 management address """
        ipv6_words = controller_settings.MGMT_IPV6_PREFIX.split(':')[:3]
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
    
    def get_host(self, island=None):
        """ Returns tincd host file """
        host = []
        for addr in self.addresses.all():
            line = "Address = %s %d" % (addr.addr, addr.port)
            if island and addr.island == island:
                # Give preference to addresses of the island, if required
                host.insert(0, line)
            else:
                host.append(line)
        host.append("Subnet = %s\n" % self.subnet.strNormal())
        if self.pubkey:
            host.append("%s" % self.pubkey)
        return '\n'.join(host)


class TincAddress(models.Model):
    """
    Describes an IP Address of a Tinc Server.
    """
    addr = models.CharField('address', max_length=128,
            help_text='The tinc IP address or host name of the host this one connects to.',
            validators=[OrValidator([validators.validate_ipv4_address, validate_host_name])])
    port = models.SmallIntegerField(default=settings.TINC_PORT_DFLT,
            help_text='TCP/UDP port of this tinc address.')
    island = models.ForeignKey('nodes.Island', null=True, blank=True,
            help_text='<a href="http://wiki.confine-project.eu/arch:rest-api#island_'
                      'at_server">Island</a> this tinc address is reachable from.')
    server = models.ForeignKey(TincServer, related_name='addresses')
    
    class Meta:
        verbose_name_plural = 'tinc addresses'
    
    def __unicode__(self):
        return str(self.addr)
    
    def save(self, *args, **kwargs):
        super(TincAddress, self).save(*args, **kwargs)
        defer(update_tincd.delay)
    
    def delete(self, *args, **kwargs):
        super(TincAddress, self).delete(*args, **kwargs)
        defer(update_tincd.delay)
    
    @property
    def name(self):
        return self.server.name


class TincClient(TincHost):
    """
    Describes a Tinc Client in the testbed. A tinc client can be a testbed node
    or a host.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return u'%s_%s' % (self.content_type.model, self.object_id)
    
    @property
    def address(self):
        """ Calculates IPV6 management address """
        ipv6_words = controller_settings.MGMT_IPV6_PREFIX.split(':')[:3]
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
    
    def get_host(self):
        """ Returns tincd hosts file content """
        host = "Subnet = %s" % self.subnet.strNormal()
        if self.pubkey:
            host += "\n\n%s" % self.pubkey
        return host
    
    def get_config(self):
        """
        Returns client tinc.conf file content, prioritizing island related gateways
        """
        config = ["Name = %s" % self.name]
        for server in self.connect_to.all():
            line = "ConnectTo = %s" % server.name
            tinc_island = self.content_object.island
            has_island = server.addresses.filter(island=tinc_island).exists()
            if tinc_island and has_island:
                config.insert(0, line)
            else:
                config.append(line)
        return '\n'.join(config)
    
    def generate_key(self, commit=False):
        bob = Bob()
        bob.gen_key()
        if commit:
            self.pubkey = bob.get_pub_key(format='X.501')
            self.save()
        return bob.get_key(format='X.501')


# Monkey-Patching Section

# Hook TincClient support to Node
@property
def tinc(self):
    ct = ContentType.objects.get_for_model(self)
    obj, __ = TincClient.objects.get_or_create(object_id=self.pk, content_type=ct)
    return obj

Node.add_to_class('related_tincclient', generic.GenericRelation('tinc.TincClient'))
Node.add_to_class('tinc', tinc)

# Hook TincServer support to Server
@property
def tinc(self):
    ct = ContentType.objects.get_for_model(self)
    obj, __ = TincServer.objects.get_or_create(object_id=self.pk, content_type=ct)
    return obj

Server.add_to_class('related_tincserver', generic.GenericRelation('tinc.TincServer'))
Server.add_to_class('tinc', tinc)

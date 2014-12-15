from django.conf import settings as base_settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import models
from django.db.models.signals import post_save, post_delete
from django_transaction_signals import defer

from controller import settings as controller_settings
from controller.models.fields import RSAPublicKeyField
from controller.models.utils import generate_chainer_manager
from controller.core.validators import validate_host_name, validate_name, OrValidator
from mgmtnetworks.models import get_mgmt_net
from nodes.models import Server, Node
from pki import Bob

from . import settings
from .tasks import update_tincd

def get_tinc(self):
    """ Get or create (without pubkey) the related tinc object """
    ct = ContentType.objects.get_for_model(self)
    obj, _ = TincHost.objects.get_or_create(object_id=self.pk, content_type=ct)
    return obj


class Host(models.Model):
    """
    Describes an odd host computer connected to the testbed (through the 
    management network) with a known administrator.
    """
    name = models.CharField(max_length=256, unique=True,
            help_text='The unique name for this host. A single non-empty line of '
                      'free-form text with no whitespace surrounding it.',
            validators=[validate_name])
    description = models.TextField(blank=True,
            help_text='An optional free-form textual description of this host.')
    owner = models.ForeignKey(base_settings.AUTH_USER_MODEL, related_name='tinc_hosts',
            help_text='The user who administrates this host (its creator by default)')
    island = models.ForeignKey('nodes.Island', null=True, blank=True,
            on_delete=models.SET_NULL,
            help_text='An optional island used to hint where this tinc client reaches to.')
    related_tinc = generic.GenericRelation('tinc.TincHost')
    related_mgmtnet = generic.GenericRelation('mgmtnetworks.MgmtNetConf')

    tinc = property(get_tinc)
    mgmt_net = property(get_mgmt_net)
    
    def __unicode__(self):
        return self.name


class TincHostQuerySet(models.query.QuerySet):
    def hosts(self, *args, **kwargs):
        server_ct = ContentType.objects.get_for_model(Server)
        return self.exclude(content_type=server_ct).filter(*args, **kwargs)
    
    def servers(self, *args, **kwargs):
        """Returns TincHosts with TincAddress."""
        return self.filter(addresses__isnull=False, *args, **kwargs).distinct()


def get_default_gateway():
    server_ctype = ContentType.objects.get_for_model(Server)
    try:
        server_id = Server.objects.get_default().pk
    except Server.DoesNotExist:
        return None
    try:
        return TincHost.objects.get(content_type=server_ctype, object_id=server_id)
    except TincHost.DoesNotExist:
        return None


class TincHost(models.Model):
    """
    Describes a Tinc Host in the testbed. Includes the tinc backend
    configuration data for this host. Unlike previous versions, there
    aren't separate classes for tinc clients and tinc servers. Now the
    unique difference is that the tinc hosts acting as servers have a
    non empty array of addresses.

    """
    name = models.CharField(max_length=32, unique=True,
            help_text='The name given to this host in the tinc network, '
                      'usually TYPE_ID (e.g. server_4).')
    pubkey = RSAPublicKeyField('public Key', unique=True, null=True, blank=True,
            help_text='PEM-encoded RSA public key used on tinc management network.')
    default_connect_to = models.ForeignKey('self', default=get_default_gateway,
            limit_choices_to={'addresses__isnull': False}, null=True, blank=True,
            on_delete=models.PROTECT)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    objects = generate_chainer_manager(TincHostQuerySet)
    
    class Meta:
        ordering = ['content_type', 'object_id']
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        name = self.name if self.name else self._name
        return '%s (%s)' % (name, self.content_object)
    
    @property
    def _name(self):
        return u'%s_%s' % (self.content_type.model, self.object_id)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # generate and initialize name
            if not self.name:
                self.name = self._name
            # Try to restore object to allow update in nested serialization
            try:
                obj = TincHost.objects.get(content_type_id=self.content_type_id,
                                           object_id=self.object_id)
            except TincHost.DoesNotExist:
                pass
            else:
                self.pk = obj.pk
        super(TincHost, self).save(*args, **kwargs)
        defer(update_tincd.delay)
    
    def delete(self, *args, **kwargs):
        super(TincHost, self).delete(*args, **kwargs)
        defer(update_tincd.delay)

    @property
    def address(self):
        return self.content_object.mgmt_net.addr
    
    @property
    def subnet(self):
        if self.content_type.model == 'node':
            return self.address.make_net(64)
        else: #self.content_type.model == [host|server]
            return self.address

    @property
    def connect_to(self):
        """
        Returns TincHosts with TincAddress that can be used
        on tincd ConnectTo configuration option.
        """
        return TincHost.objects.servers()
    
    def get_host(self, island=None):
        # Ignore orphan TincHost objects that prevent proper update_tincd!
        if self.content_object is None:
            return ''
        ct_model = self.content_type.model
        if ct_model == 'node' or ct_model == 'host':
            # Returns tincd hosts file content
            host = "Subnet = %s" % self.subnet.strNormal()
            if self.pubkey:
                host += "\n\n%s" % self.pubkey
            return host
        elif ct_model == 'server':
            # Returns tincd host file
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
    
    def get_config(self):
        """
        Returns client tinc.conf file content based on default
        tinc gatway configured.
        """
        if self.content_type.model == 'server':
            raise TypeError("Cannot get_config from a server.")
        config = [
            "Name = %s" % self.name,
            "ConnectTo = %s" % self.default_connect_to.name
        ]
        return '\n'.join(config)

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
    
    def generate_key(self, commit=False):
        if self.content_type.model == 'server':
            raise TypeError("Cannot generate_key from a server.")
        bob = Bob()
        bob.gen_key()
        if commit:
            self.pubkey = bob.get_pub_key(format='X.501')
            self.save()
        return bob.get_key(format='X.501')


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
            on_delete=models.SET_NULL,
            help_text='<a href="http://wiki.confine-project.eu/arch:rest-api#island_'
                      'at_server">Island</a> this tinc address is reachable from.')
    host = models.ForeignKey(TincHost, related_name='addresses')
    
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


###  Signals  ###

# update the node set_state on tinc config update
def tinchost_changed(sender, instance, **kwargs):
    # Do nothing while loading fixtures or running migrations
    if kwargs.get('raw', False):
        return
    if hasattr(instance.content_object, 'update_set_state'): # is a node
        instance.content_object.update_set_state()

post_save.connect(tinchost_changed, sender=TincHost)
post_delete.connect(tinchost_changed, sender=TincHost)


# Monkey-Patching Section
tinc = property(get_tinc)

# Hook TincHost support to Node

Node.add_to_class('related_tinc', generic.GenericRelation('tinc.TincHost'))
Node.add_to_class('tinc', tinc)

# Hook TincHost support to Server
Server.add_to_class('related_tinc', generic.GenericRelation('tinc.TincHost'))
Server.add_to_class('tinc', tinc)

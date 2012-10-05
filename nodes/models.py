from common import fields
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
import settings
from singleton_models.models import SingletonModel
from tinc.models import Gateway, TincClient


class Node(models.Model):
    STATES = (('install_conf', _('Install Configuration')),
              ('install_cert', _('Install Certificate')),
              ('debug', _('Debug')),
              ('failure', _('Failure')),
              ('safe', _('Safe')),
              ('production', _('Production')),)

    description = models.CharField(max_length=256)
    admin = models.ForeignKey(User, help_text="""The user who administrates this 
        node (its creator by default).""")
    priv_ipv4_prefix = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True,
        help_text="""An IPv4 /24 network in CIDR notation used as a node private IPv4 prefix. 
        See <a href="http://wiki.confine-project.eu/arch:addressing">addressing</a> 
        for legal values. When null, use the default value provided in 
        <a href="http://wiki.confine-project.eu/arch:rest-api#base_at_server">testbed 
        parameters</a>.""")
    sliver_mac_prefix = models.PositiveSmallIntegerField(max_length=16, null=True, blank=True,
        help_text="""A 16-bit integer number in 0x-prefixed hexadecimal notation
        used as the node sliver MAC prefix. See 
        <a href="http://wiki.confine-project.eu/arch:addressing">addressing</a> 
        for legal values. When null, use the default value provided in 
        <a href="http://wiki.confine-project.eu/arch:rest-api#base_at_server">testbed 
        parameters</a>.""")
    sliver_pub_ipv4_total = models.IntegerField(help_text="""The total number of public 
        (from the point of view of the CN) IPv4 addresses available in this node's local 
        network to be allocated to slivers' public interfaces (see <a 
        href="http://wiki.confine-project.eu/arch:node">node</a> architecture). 
        If the local network uses private addresses the value should be 0.""")
    cn_url = models.URLField(blank=True, help_text="""An optional URL pointing to 
        a description of this node in its CN's node DB web application.""")
    cndb_uri = models.CharField(max_length=256, blank=True, help_text="""An 
        optional URI for this node in its CN's CNDB REST API.""")
    cndb_cached_on = models.DateTimeField(null=True, blank=True)
    set_state = models.CharField(max_length=16, choices=STATES, default='install_conf')

    def __unicode__(self):
        return self.description


class NodeProp(models.Model):
    node = models.ForeignKey(Node)
    name = models.CharField(max_length=32, unique=True)
    value = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class Host(TincClient):
    description = models.CharField(max_length=256)
    admin = models.ForeignKey(User)


class CnHost(models.Model):
    cn_url = models.URLField(blank=True)
    cndb_uri = models.CharField(max_length=256, blank=True)
    cndb_cached_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return str(self.pk)


class ResearchDevice(CnHost, TincClient):
    uuid = fields.UUIDField(auto=True, primary_key=True)
    node = models.OneToOneField(Node)
    pubkey = models.TextField(unique=True, blank=True, verbose_name="Public Key")
    cert = models.TextField(unique=True, blank=True, verbose_name="Certificate")
    arch = models.CharField(verbose_name="Architecture", max_length=16, 
        choices=settings.RESEARCH_DEVICE_ARCHS, default=settings.DEFAULT_RESEARCH_DEVICE_ARCH)
    boot_sn = models.IntegerField(verbose_name="Boot Sequence Number", default=0,
        help_text=_("Number of times this node's RD has been instructed to be rebooted"))
    local_iface = models.CharField(verbose_name="Local Interface", max_length=16, default='eth0',
        help_text="""Name of the interface used as a local interface. See <a href="wiki.confine-project.eu/arch:node">node architecture</a>.""")

    def __unicode__(self):
        return str(self.uuid)


class RdDirectIface(models.Model):
    name = models.CharField(max_length=16)
    rd = models.ForeignKey(ResearchDevice)
    
    class Meta:
        unique_together = ['name', 'rd']
    
    def __unicode__(self):
        return self.name


class Server(SingletonModel, Gateway):
    #TODO: ID = 2
    class Meta:
        verbose_name = "Server"
        verbose_name_plural = "Server"

    def __unicode__(self):
        return 'Server'

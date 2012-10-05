from common import fields
from django.contrib.auth.models import User
from django.db import models
import settings
from singleton_models.models import SingletonModel


class Node(models.Model):
    STATES = (('install_conf', 'Install Configuration'),
              ('install_cert', 'Install Certificate'),
              ('debug', 'Debug'),
              ('failure', 'Failure'),
              ('safe', 'Safe'),
              ('production', 'Production'),)

    description = models.CharField(max_length=256)
    admin = models.ForeignKey(User, help_text="""The user who administrates this 
        node (its creator by default).""")
    priv_ipv4_prefix = models.GenericIPAddressField(protocol='IPv4', null=True, 
        blank=True, help_text="""IPv4 /24 network in CIDR notation used as a node 
        private IPv4 prefix. See <a href="http://wiki.confine-project.eu/arch:addressing">
        addressing</a> for legal values. When null, use the default value provided in 
        <a href="http://wiki.confine-project.eu/arch:rest-api#base_at_server">
        testbed parameters</a>.""")
    sliver_mac_prefix = models.PositiveSmallIntegerField(max_length=16, null=True,
        blank=True, help_text="""A 16-bit integer number in 0x-prefixed hexadecimal 
        notation used as the node sliver MAC prefix. See 
        <a href="http://wiki.confine-project.eu/arch:addressing">addressing</a> 
        for legal values. When null, use the default value provided in 
        <a href="http://wiki.confine-project.eu/arch:rest-api#base_at_server">
        testbed parameters</a>.""")
    sliver_pub_ipv4_total = models.IntegerField(help_text="""Total number of public 
        (from the point of view of the CN) IPv4 addresses available in this node's 
        local network to be allocated to slivers' public interfaces (see <a 
        href="http://wiki.confine-project.eu/arch:node">node</a> architecture). 
        If the local network uses private addresses the value should be 0.""")
    cn_url = models.URLField(blank=True, help_text="""An optional URL pointing to 
        a description of this node in its CN's node DB web application.""")
    cndb_uri = models.CharField(max_length=256, blank=True, 
        help_text="""An optional URI for this node in its CN's CNDB REST API.""")
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


class CnHost(models.Model):
    cn_url = models.URLField(blank=True)
    cndb_uri = models.CharField(max_length=256, blank=True)
    cndb_cached_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return str(self.pk)


class ResearchDevice(CnHost):
    uuid = fields.UUIDField(auto=True, primary_key=True, help_text="""A universally 
        unique identifier (UUID, RFC 4122).""")
    node = models.OneToOneField(Node)
    pubkey = models.TextField(unique=True, blank=True, help_text="""A PEM-encoded 
        RSA public key for this RD (used by SFA).""")
    cert = models.TextField(unique=True, blank=True, help_text="""An X.509 
        PEM-encoded certificate for this RD. The certificate may be signed by a 
        CA recognised in the testbed and required by clients and services accessing 
        the node API.""")
    arch = models.CharField(max_length=16, choices=settings.RESEARCH_DEVICE_ARCHS, 
        default=settings.DEFAULT_RESEARCH_DEVICE_ARCH, help_text="""Architecture 
        of this RD (as reported by uname -m).""")
    boot_sn = models.IntegerField(default=0, help_text="""Number of times this 
        RD has been instructed to be rebooted.""")
    local_iface = models.CharField(verbose_name="Local Interface", max_length=16, 
        default='eth0', help_text="""Name of the interface used as a local interface. 
        See <a href="wiki.confine-project.eu/arch:node">node architecture</a>.""")

    def __unicode__(self):
        return str(self.uuid)


class RdDirectIface(models.Model):
    name = models.CharField(max_length=16)
    rd = models.ForeignKey(ResearchDevice)
    
    class Meta:
        unique_together = ['name', 'rd']
    
    def __unicode__(self):
        return self.name


class Server(SingletonModel, CnHost):
    class Meta:
        verbose_name = "Server"
        verbose_name_plural = "Server"

    def __unicode__(self):
        return 'Server'

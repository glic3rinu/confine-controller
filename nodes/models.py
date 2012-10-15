from django_extensions.db import fields
from django.contrib.auth.models import User
from django.db import models
from nodes import settings
from singleton_models.models import SingletonModel


class CnHost(models.Model):
    cn_url = models.URLField(blank=True)
    cndb_uri = models.CharField(max_length=256, blank=True)
    cndb_cached_on = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return str(self.pk)


class Node(CnHost):
    STATES = (('install_conf', 'Install Configuration'),
              ('install_cert', 'Install Certificate'),
              ('debug', 'Debug'),
              ('failure', 'Failure'),
              ('safe', 'Safe'),
              ('production', 'Production'),)
    
    uuid = fields.UUIDField(auto=True, help_text="""A universally unique 
        identifier (UUID, RFC 4122).""")
    pubkey = models.TextField(unique=True, null=True, blank=True, help_text="""A 
        PEM-encoded RSA public key for this RD (used by SFA).""")
    cert = models.TextField(unique=True, null=True, blank=True, help_text="""An 
        X.509 PEM-encoded certificate for this RD. The certificate may be signed 
        by a CA recognised in the testbed and required by clients and services 
        accessing the node API.""")
    description = models.CharField(max_length=256)
    arch = models.CharField(max_length=16, choices=settings.NODE_ARCHS, 
        default=settings.DEFAULT_NODE_ARCH, help_text="""Architecture 
        of this RD (as reported by uname -m).""")
    local_iface = models.CharField(verbose_name="Local Interface", max_length=16, 
        default='eth0', help_text="""Name of the interface used as a local interface. 
        See <a href="wiki.confine-project.eu/arch:node">node architecture</a>.""")
    priv_ipv4_prefix = models.GenericIPAddressField(protocol='IPv4', null=True, 
        blank=True, help_text="""IPv4 /24 network in CIDR notation used as a node 
        private IPv4 prefix. See <a href="http://wiki.confine-project.eu/arch:addressing">
        addressing</a> for legal values. %s When null.""" % settings.PRIV_IPV4_PREFIX_DFLT)
    # TODO restric this according the data model
    sliver_mac_prefix = models.PositiveSmallIntegerField(max_length=16, null=True,
        blank=True, help_text="""A 16-bit integer number in 0x-prefixed hexadecimal 
        notation used as the node sliver MAC prefix. See 
        <a href="http://wiki.confine-project.eu/arch:addressing">addressing</a> 
        for legal values. %s when null.</a>.""" % settings.SLIVER_MAC_PREFIX_DFLT)
    sliver_pub_ipv4_total = models.IntegerField(default=0, help_text="""Total number 
        of public (from the point of view of the CN) IPv4 addresses available in 
        this node's local network to be allocated to slivers' public interfaces (see 
        <a href="http://wiki.confine-project.eu/arch:node">node</a> architecture). 
        If the local network uses private addresses the value should be 0.""")
    boot_sn = models.IntegerField(default=0, blank=True, help_text="""Number of 
        times this RD has been instructed to be rebooted.""")
    set_state = models.CharField(max_length=16, choices=STATES, default='install_conf')
    admin = models.ForeignKey(User, help_text="""The user who administrates this 
        node (its creator by default).""")
    
    def __unicode__(self):
        return str(self.id)
    
    def clean(self):
        """ Empty pubkey and cert as NULL instead of empty string """
        if self.pubkey is u'': self.pubkey = None
        if self.cert is u'': self.cert = None
        super(Node, self).clean()
    
    @property
    def properties(self):
        return dict(self.nodeprop_set.all().values_list('name', 'value'))
    
    @property
    def slivers(self):
        return self.sliver_set.all()


class NodeProp(models.Model):
    node = models.ForeignKey(Node)
    name = models.CharField(max_length=32, unique=True)
    value = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.name


class DirectIface(models.Model):
    name = models.CharField(max_length=16)
    node = models.ForeignKey(Node)
    
    class Meta:
        unique_together = ['name', 'node']
    
    def __unicode__(self):
        return self.name


class Server(SingletonModel, CnHost):
    class Meta:
        verbose_name = "server"
        verbose_name_plural = "server"
    
    def __unicode__(self):
        return 'Server'

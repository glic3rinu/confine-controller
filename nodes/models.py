import re

from django_extensions.db import fields
from django_transaction_signals import defer
from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from singleton_models.models import SingletonModel

from nodes import settings


class Node(models.Model):
    """
    Describes a node in the testbed.
    
    See Node architecture: http://wiki.confine-project.eu/arch:node
    """
    INSTALL_CONF = 'install_conf'
    INSTALL_CERT = 'install_cert'
    DEBUG = 'debug'
    FAILURE = 'failure'
    SAFE = 'safe'
    PRODUCTION = 'production'
    STATES = ((INSTALL_CONF, 'Install Configuration'),
              (INSTALL_CERT, 'Install Certificate'),
              (DEBUG, 'Debug'),
              (FAILURE, 'Failure'),
              (SAFE, 'Safe'),
              (PRODUCTION, 'Production'),)
    
    uuid = fields.UUIDField(auto=True, 
        help_text='Universally unique identifier (UUID, RFC 4122).')
    pubkey = models.TextField('Public Key', unique=True, null=True, blank=True, 
        help_text='PEM-encoded RSA public key for this RD (used by SFA).')
    cert = models.TextField('Certificate', unique=True, null=True, blank=True, 
        help_text='X.509 PEM-encoded certificate for this RD. The certificate '
                  'may be signed by a CA recognised in the testbed and required '
                  'by clients and services accessing the node API.')
    description = models.CharField(max_length=256,
        help_text='Free-form textual description of this host/device.')
    arch = models.CharField('Architecture', max_length=16,
        choices=settings.NODE_ARCHS, default=settings.DEFAULT_NODE_ARCH,
        help_text='Architecture of this RD (as reported by uname -m).',)
    local_iface = models.CharField('Local Interface', max_length=16, 
        default=settings.DEFAULT_NODE_LOCAL_IFACE,
        help_text='Name of the interface used as a local interface. See <a href='
                  '"wiki.confine-project.eu/arch:node">node architecture</a>.')
    priv_ipv4_prefix = models.GenericIPAddressField('Private IPv4 Prefix', 
        protocol='IPv4', null=True, blank=True,
        help_text='IPv4 /24 network in CIDR notation used as a node private IPv4 '
                  'prefix. See <a href="http://wiki.confine-project.eu/arch:'
                  'addressing">addressing</a> for legal values. %s When null.' 
                  % settings.PRIV_IPV4_PREFIX_DFLT)
    # TODO restric this according the data model
    sliver_mac_prefix = models.PositiveSmallIntegerField('Sliver MAC Prefix',
        max_length=16, null=True, blank=True,
        help_text='A 16-bit integer number in 0x-prefixed hexadecimal notation '
                  'used as the node sliver MAC prefix. See <a href="http://wiki.'
                  'confine-project.eu/arch:addressing">addressing</a> for legal '
                  'values. %s when null.</a>.' % settings.SLIVER_MAC_PREFIX_DFLT)
    sliver_pub_ipv4_total = models.IntegerField('Sliver Public IPv4 Total', default=0,
        help_text='Total number of public (from the point of view of the CN) '
                  'IPv4 addresses available in this node\'s local network to be '
                  'allocated to slivers\' public interfaces (see <a href="http:'
                  '//wiki.confine-project.eu/arch:node">node</a> architecture). '
                  'If the local network uses private addresses the value should '
                  'be 0.')
    boot_sn = models.IntegerField('Boot Sequence Number', default=0, blank=True, 
        help_text='Number of times this RD has been instructed to be rebooted.')
    set_state = models.CharField(max_length=16, choices=STATES, default=INSTALL_CONF)
    admin = models.ForeignKey(User, 
        help_text='User who administrates this node (its creator by default).')
    
    def __unicode__(self):
        return self.description
    
    def clean(self):
        """ Empty pubkey and cert as NULL instead of empty string """
        if self.pubkey == u'': self.pubkey = None
        if self.cert == u'': self.cert = None
        super(Node, self).clean()
    
    @property
    def properties(self):
        return dict(self.nodeprop_set.all().values_list('name', 'value'))
    
    @property
    def slivers(self):
        return self.sliver_set.all()
    
    @property
    def direct_ifaces(self):
        return self.directiface_set.all()
    
    def reboot(self):
        self.boot_sn += 1
        self.save()
    
    @property
    def ipv6_local_addr(self):
        # X:Y:Z:N:0000::2/64
        ipv6_words = settings.MGMT_IPV6_PREFIX.split(':')[:3] # X:Y:Z
        ipv6_words.extend([
            '%.4x' % self.id, # N (Node.id in hexadecimal)
            '0000::2'
        ])
        return ':'.join(ipv6_words)
    
    def get_sliver_mac_prefix(self):
        if self.sliver_mac_prefix: 
            return self.sliver_mac_prefix
        return settings.SLIVER_MAC_PREFIX_DFLT
    
    def get_sliver_mac_prefix(self):
        if self.sliver_mac_prefix: 
            return self.sliver_mac_prefix
        return settings.SLIVER_MAC_PREFIX_DFLT
    
    def get_priv_ipv4_prefix(self):
        if self.priv_ipv4_prefix:
            return self.priv_ipv4_prefix
        return settings.PRIV_IPV4_PREFIX_DFLT


class NodeProp(models.Model):
    """ 
    A mapping of (non-empty) arbitrary node property names to their (string) 
    values.
    """
    node = models.ForeignKey(Node)
    name = models.CharField(max_length=32,
        help_text='Per node unique single line of free-form text with no '
                  'whitespace surrounding it',
        validators=[validators.RegexValidator(re.compile('^[a-z][_0-9a-z]*[0-9a-z]$'), 
                   'Enter a valid property name.', 'invalid')])
    value = models.CharField(max_length=256)
    
    class Meta:
        unique_together = ('node', 'name')
    
    def __unicode__(self):
        return self.name


class DirectIface(models.Model):
    """
    Interfaces used as direct interfaces. 
    
    See node architecture: http://wiki.confine-project.eu/arch:node
    """
    name = models.CharField(max_length=16)
    node = models.ForeignKey(Node)
    
    class Meta:
        unique_together = ['name', 'node']
    
    def __unicode__(self):
        return self.name


class Server(SingletonModel):
    """
    Describes the testbed server (controller).
    """
    description = models.CharField(max_length=256,
        help_text='Free-form textual description of the server.')
    
    class Meta:
        verbose_name = "server"
        verbose_name_plural = "server"
    
    def __unicode__(self):
        return 'Server'

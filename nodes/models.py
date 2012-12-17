import re

from django_extensions.db import fields
from django_transaction_signals import defer
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from singleton_models.models import SingletonModel

from common.validators import UUIDValidator, RSAPublicKeyValidator, NetIfaceNameValidator

from . import settings
from .validators import SliverMacPrefixValidator, Ipv4Range


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
    STATES = (
        (INSTALL_CONF, 'Install Configuration'),
        (INSTALL_CERT, 'Install Certificate'),
        (DEBUG, 'Debug'),
        (FAILURE, 'Failure'),
        (SAFE, 'Safe'),
        (PRODUCTION, 'Production'),
    )
    IPV6_METHODS = (
        ('none', 'none'),
        ('dhcp', 'dhcp'),
        ('auto', 'auto'),
    )
    IPV4_METHODS = (
        ('none', 'none'),
        ('dhcp', 'dhcp'),
        ('range', 'range'),
    )
    
    name = models.CharField(max_length=256, unique=True,
        help_text='A unique name for this node. A single non-empty line of '
                  'free-form text with no whitespace surrounding it. matching '
                  'the regular expression',
        validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'), 
                   'Enter a valid name.', 'invalid')])
    uuid = models.CharField(max_length=36, unique=True, blank=True, null=True,
        help_text='A universally unique identifier (UUID, RFC 4122) for this node '
                  '(used by SFA). This is optional, but once set to a valid UUID '
                  'it can not be changed.', validators=[UUIDValidator])
    pubkey = models.TextField('Public Key', unique=True, null=True, blank=True, 
        help_text='PEM-encoded RSA public key for this RD (used by SFA).',
        validators=[RSAPublicKeyValidator])
    cert = models.TextField('Certificate', unique=True, null=True, blank=True, 
        help_text='X.509 PEM-encoded certificate for this RD. The certificate '
                  'may be signed by a CA recognised in the testbed and required '
                  'by clients and services accessing the node API.')
    description = models.TextField(blank=True,
        help_text='Free-form textual description of this host/device.')
    arch = models.CharField('Architecture', max_length=16,
        choices=settings.NODE_ARCHS, default=settings.DEFAULT_NODE_ARCH,
        help_text='Architecture of this RD (as reported by uname -m).',)
    local_iface = models.CharField('Local Interface', max_length=16, 
        default=settings.DEFAULT_NODE_LOCAL_IFACE, validators=[NetIfaceNameValidator],
        help_text='Name of the interface used as a local interface. See <a href='
                  '"wiki.confine-project.eu/arch:node">node architecture</a>.')
    sliver_pub_ipv6 = models.CharField('Sliver Public IPv6', max_length=8,
        help_text='Indicates IPv6 support for public sliver interfaces in the '
                  'local network (see <a href="https://wiki.confine-project.eu/'
                  'arch:node">node architecture</a>). Possible values: none (no '
                  'public IPv6 support), dhcp (addresses configured using DHCPv6), '
                  'auto (addresses configured using NDP stateless autoconfiguration).',
        default='none', choices=IPV6_METHODS)
    sliver_pub_ipv4 = models.CharField('Sliver Public IPv4', max_length=8,
        help_text='Indicates IPv4 support for public sliver interfaces in the '
                  'local network (see <a href="https://wiki.confine-project.eu/'
                  'arch:node">node architecture</a>). Possible values: none (no '
                  'public IPv4 support), dhcp (addresses configured using DHCP), '
                  'range (addresses chosen from a range, see sliver_pub_ipv4_range).',
        default='none', choices=IPV4_METHODS)
    sliver_pub_ipv4_range = models.CharField('Sliver Public IPv4 Range', 
        help_text='Describes the public IPv4 range that can be used by sliver '
                  'public interfaces. If /sliver_pub_ipv4 is none, its value is '
                  'null. If /sliver_pub_ipv4 is dhcp, its value is #N, where N '
                  'is the decimal integer number of DHCP addresses reserved for '
                  'slivers. If /sliver_pub_ipv4 is range, its value is BASE_IP#N, '
                  'where N is the decimal integer number of consecutive addresses '
                  'reserved for slivers after and including the range\'s base '
                  'address BASE_IP (an IP address in the local network).',
        max_length=256, blank=True, null=True, validators=[Ipv4Range])
    sliver_mac_prefix = models.CharField('Sliver MAC Prefix', null=True,
        blank=True, max_length=5, validators=[SliverMacPrefixValidator],
        help_text='A 16-bit integer number in 0x-prefixed hexadecimal notation '
                  'used as the node sliver MAC prefix. See <a href="http://wiki.'
                  'confine-project.eu/arch:addressing">addressing</a> for legal '
                  'values. %s when null.</a>.' % settings.SLIVER_MAC_PREFIX_DFLT)
    priv_ipv4_prefix = models.GenericIPAddressField('Private IPv4 Prefix', 
        protocol='IPv4', null=True, blank=True,
        help_text='IPv4 /24 network in CIDR notation used as a node private IPv4 '
                  'prefix. See <a href="http://wiki.confine-project.eu/arch:'
                  'addressing">addressing</a> for legal values. %s When null.' 
                  % settings.PRIV_IPV4_PREFIX_DFLT)
    boot_sn = models.IntegerField('Boot Sequence Number', default=0, blank=True, 
        help_text='Number of times this RD has been instructed to be rebooted.')
    set_state = models.CharField(max_length=16, choices=STATES, default=INSTALL_CONF)
    group = models.ForeignKey('users.Group', 
        help_text='The group this node belongs to. The user creating this node '
                  'must be an administrator or technician of this group, and the '
                  'group must have node creation allowed (/allow_nodes=true). '
                  'Administrators and technicians in this group are able to '
                  'manage this node.')
    
    def __unicode__(self):
        return self.name
    
    def clean(self):
        """ 
        Empty pubkey, cert and sliver_pub_ipv4_range as NULL instead of empty string.
        """
        if self.pubkey == '': self.pubkey = None
        if self.cert == '': self.cert = None
        if self.uuid == '': self.uuid = None
        if self.sliver_pub_ipv4 == 'none':
            if self.sliver_pub_ipv4_range == '' or self.sliver_pub_ipv4_range is None:
                self.sliver_pub_ipv4_range = None
            else:
                raise ValidationError("If 'Sliver Public IPv4 is 'none' then Sliver "
                                      "Public IPv4 Range must be empty")
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
    
    def get_sliver_mac_prefix(self):
        if self.sliver_mac_prefix: 
            return self.sliver_mac_prefix
        return settings.SLIVER_MAC_PREFIX_DFLT
    
    def get_priv_ipv4_prefix(self):
        if self.priv_ipv4_prefix:
            return self.priv_ipv4_prefix
        return settings.PRIV_IPV4_PREFIX_DFLT
    
    @property
    def max_pub4ifaces(self):
        """
        Obtains the number of availables IPs type 4 for the sliver
          + When Node.sliver_pub_ipv4 is dhcp, its value is #N, meaning there
          are N total public IPv4 addresses for slivers.
          + When Node.sliver_pub_ipv4 is range, its value is IP#N
          meaning there are N total public IPv4 addresses for slivers after and
          including IP or B.
          + When Node.sliver_pub_ipv4 is none there are not support for public ipv4
        """
        if self.sliver_pub_ipv4 == 'none':
            max_num = 0
        else: # dhcp | range
            max_num = int(self.sliver_pub_ipv4_range.split('#')[1])
        return max_num
    
    @property
    def sliver_pub_ipv4_avail(self):
        if not self.sliver_pub_ipv4_range:
            return 0
        else:
            return self.sliver_pub_ipv4_range.split('#')[1]


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
        verbose_name = 'Node Property'
        verbose_name_plural = 'Node Properties'
    
    def __unicode__(self):
        return self.name


class DirectIface(models.Model):
    """
    Interfaces used as direct interfaces. 
    
    See node architecture: http://wiki.confine-project.eu/arch:node
    """
    name = models.CharField(max_length=16, validators=[NetIfaceNameValidator],
        help_text='he name of the interface used as a local interface (non-empty). '
                  'See <a href="https://wiki.confine-project.eu/arch:node">node '
                  'architecture</a>.')
    node = models.ForeignKey(Node)
    
    class Meta:
        unique_together = ['name', 'node']
        verbose_name = 'Direct Network Interface'
        verbose_name_plural = 'Direct Network Interfaces'
    
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

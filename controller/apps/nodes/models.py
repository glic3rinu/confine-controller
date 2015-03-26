from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.db.models.signals import post_save, post_delete

from controller.models.fields import NullableCharField, PEMCertificateField
from controller.settings import PRIV_IPV6_PREFIX, PRIV_IPV4_PREFIX_DFLT, SLIVER_MAC_PREFIX_DFLT
from controller.core.validators import validate_name, validate_prop_name, validate_net_iface_name, validate_net_iface_name_with_vlan
from pki import Bob

from . import settings
from .helpers import url_on_mgmt_net
from .validators import (validate_sliver_mac_prefix, validate_ipv4_range,
        validate_dhcp_range, validate_priv_ipv4_prefix)


class Api(models.Model):
    base_uri = models.URLField('base URI', max_length=256,
            help_text='The base URI of the API endpoint.')
    cert = PEMCertificateField('Certificate', null=True, blank=True,
            help_text='An optional X.509 PEM-encoded certificate for the API '
                      'endpoint. Providing this may save API clients from '
                      'checking the API certificate\'s signature.')
    
    class Meta:
        abstract = True
    
    def clean(self):
        super(Api, self).clean()
        # base_uri SHOULD always end with slash '/'
        if not self.base_uri.endswith('/'):
            self.base_uri += '/'


class NodeApiManager(models.Manager):
    def create_default(self, node, cert=None):
        base_uri = NodeApi.default_base_uri(node)
        return self.create(node=node, base_uri=base_uri, cert=cert)


class NodeApi(Api):
    """
    Data on the endpoint that can be used to access this node's REST API.
    Please note that the API may be offered by another host (e.g. a caching
    proxy), which doesn't preclude the node from running the API itself as
    well (e.g. on its management network address).

    """
    NODE = 'node'
    TYPES = ((NODE, 'Node'),)
    
    type = models.CharField(max_length=16, choices=TYPES, default=NODE)
    node = models.OneToOneField('nodes.Node', primary_key=True, related_name='_api')
    
    objects = NodeApiManager()
    
    class Meta:
        verbose_name = 'node API'
        verbose_name_plural = 'node API'
    
    @property
    def is_configured(self):
        if self.base_uri.startswith('https') and not self.cert:
            return False
        return True
    
    @classmethod
    def default_base_uri(cls, node):
        if node.mgmt_net is None:
            return ''
        mgmt_addr = node.mgmt_net.addr
        return settings.NODES_NODE_API_BASE_URI_DEFAULT % {'mgmt_addr': mgmt_addr}


class ServerApiManager(models.Manager):
    def create_default(self, server, type, cert=None):
        mgmt_addr = self.server.mgmt_net.addr
        base_uri = settings.NODES_SERVER_API_BASE_URI_DEFAULT % {'mgmt_addr': mgmt_addr}
        return self.create(server=server, type=type, base_uri=base_uri, cert=cert)


class ServerApi(Api):
    """
    Data on the endpoints that can be used to access this server's REST API.
    Please note that the API may be offered by another host (e.g. a caching
    proxy), which doesn't preclude the server from running the API itself as
    well (e.g. on its management network address).
    """
    REGISTRY = 'registry'
    CONTROLLER = 'controller'
    TYPES = (
        (REGISTRY, 'Registry'),
        (CONTROLLER, 'Controller'),
    )
    
    type = models.CharField(max_length=16, choices=TYPES)
    server = models.ForeignKey('nodes.Server', related_name='api')
    island = models.ForeignKey('nodes.Island', null=True, blank=True,
            on_delete=models.SET_NULL,
            help_text='An optional island used to hint where this API endpoint '
                      'is reachable from. An API endpoint reachable from the '
                      'management network may omit this member.')
    
    objects = ServerApiManager()
    
    class Meta:
        verbose_name = 'server API'
        verbose_name_plural = 'server APIs'


class Node(models.Model):
    """
    Describes a node in the testbed.
    
    See Node architecture: http://wiki.confine-project.eu/arch:node
    """
    DEBUG = 'debug'
    FAILURE = 'failure'
    SAFE = 'safe'
    PRODUCTION = 'production'
    STATES = (
        (DEBUG, 'DEBUG'),
        (SAFE, 'SAFE'),
        (PRODUCTION, 'PRODUCTION'),
        (FAILURE, 'FAILURE'),
    )
    NONE = 'none'
    DHCP = 'dhcp'
    AUTO = 'auto'
    RANGE = 'range'
    IPV6_METHODS = (
        (NONE, 'None'),
        (DHCP, 'DHCP'),
        (AUTO, 'Auto'),
    )
    IPV4_METHODS = (
        (NONE, 'None'),
        (DHCP, 'DHCP'),
        (RANGE, 'Range'),
    )
    
    name = models.CharField(max_length=256, unique=True,
            help_text='A unique name for this node. A single non-empty line of '
                      'free-form text with no whitespace surrounding it.',
            validators=[validate_name])
    description = models.TextField(blank=True,
            help_text='Free-form textual description of this host/device.')
    arch = models.CharField('Architecture', max_length=16,
            choices=settings.NODES_NODE_ARCHS, default=settings.NODES_NODE_ARCH_DFLT,
            help_text='Architecture of this RD (as reported by uname -m).',)
    local_iface = models.CharField('Local interface', max_length=16, 
            default=settings.NODES_NODE_LOCAL_IFACE_DFLT, 
            validators=[validate_net_iface_name_with_vlan],
            help_text='Name of the interface used as a local interface. See <a href='
                      '"wiki.confine-project.eu/arch:node">node architecture</a>.')
    sliver_pub_ipv6 = models.CharField('Sliver public IPv6', max_length=8,
            default='none', choices=IPV6_METHODS,
            help_text='Indicates IPv6 support for public sliver interfaces in the '
                      'local network (see <a href="https://wiki.confine-project.eu/'
                      'arch:node">node architecture</a>). Possible values: none (no '
                      'public IPv6 support), dhcp (addresses configured using DHCPv6), '
                      'auto (addresses configured using NDP stateless autoconfiguration).')
    sliver_pub_ipv4 = models.CharField('Sliver public IPv4', max_length=8,
            default=settings.NODES_NODE_SLIVER_PUB_IPV4_DFLT, choices=IPV4_METHODS,
            help_text='Indicates IPv4 support for public sliver interfaces in the '
                      'local network (see <a href="https://wiki.confine-project.eu/'
                      'arch:node">node architecture</a>). Possible values: none (no '
                      'public IPv4 support), dhcp (addresses configured using DHCP), '
                      'range (addresses chosen from a range, see <em>Sliver public IPv4 range</em>).')
    sliver_pub_ipv4_range = NullableCharField('Sliver public IPv4 range', max_length=256,
            blank=True, null=True, default=settings.NODES_NODE_SLIVER_PUB_IPV4_RANGE_DFLT,
            help_text='Describes the public IPv4 range that can be used by sliver '
                      'public interfaces. If <em>Sliver public IPv4</em> is <em>none</em>, its value is '
                      'null. If <em>Sliver public IPv4</em> is <em>dhcp</em>, its value is <em>#N</em>, where N '
                      'is the decimal integer number of DHCP addresses reserved for '
                      'slivers. If <em>Sliver public IPv4</em> is <em>range</em>, its value is <em>BASE_IP#N</em>, '
                      'where N is the decimal integer number of consecutive addresses '
                      'reserved for slivers after and including the range\'s base '
                      'address BASE_IP (an IP address in the local network).')
    sliver_mac_prefix = NullableCharField('Sliver MAC prefix', null=True,
            blank=True, max_length=5, validators=[validate_sliver_mac_prefix],
            help_text='A 16-bit integer number in 0x-prefixed hexadecimal notation '
                      'used as the node sliver MAC prefix. See <a href="http://wiki.'
                      'confine-project.eu/arch:addressing">addressing</a> for legal '
                      'values. %s when null.' % SLIVER_MAC_PREFIX_DFLT)
    priv_ipv4_prefix = NullableCharField('Private IPv4 prefix', null=True,
            blank=True, max_length=19, validators=[validate_priv_ipv4_prefix],
            help_text='IPv4 /24 network in CIDR notation used as a node private IPv4 '
                      'prefix. See <a href="http://wiki.confine-project.eu/arch:'
                      'addressing">addressing</a> for legal values. %s When null.'
                  % PRIV_IPV4_PREFIX_DFLT)
    boot_sn = models.IntegerField('Boot sequence number', default=0, blank=True, 
            help_text='Number of times this RD has been instructed to be rebooted.')
    set_state = models.CharField(max_length=16, choices=STATES, default=DEBUG,
            help_text='The state set on this node (set state). Possible values: debug '
                      '(initial), safe, production, failure. To support the late '
                      'addition or generation of node keys, the set state is forced '
                      'to remain debug while the node is missing some key, certificate '
                      'or other configuration item. The set state is automatically '
                      'changed to safe when all items are in place. Changing existing '
                      'keys also moves the node into state debug or safe as appropriate. '
                      'All set states but debug can be manually selected. See <a href='
                      '"https://wiki.confine-project.eu/arch:node-states">node states</a> '
                      'for the full description of set states and possible transitions.')
    group = models.ForeignKey('users.Group', related_name='nodes',
            help_text='The group this node belongs to. The user creating this node '
                      'must be a group or node administrator of this group, and the '
                      'group must have node creation allowed (/allow_nodes=true). '
                      'Node and group administrators in this group are able to '
                      'manage this node.')
    island = models.ForeignKey('nodes.Island', null=True, blank=True,
            on_delete=models.SET_NULL,
            help_text='An optional island used to hint where the node is located '
                      'network-wise.')
    
    def __unicode__(self):
        return self.name
    
    def clean(self):
        # clean set_state:
        if self.pk:
            old = Node.objects.get(pk=self.pk)
            if old.set_state == Node.DEBUG and self.set_state != Node.DEBUG:
                raise ValidationError("Can not manually exit from Debug state.")
            elif self.set_state == Node.DEBUG and old.set_state != Node.DEBUG:
                raise ValidationError("Can not manually enter to Debug state.")
            elif self.set_state == Node.PRODUCTION:
                if old.set_state not in [Node.SAFE, Node.PRODUCTION]:
                    raise ValidationError("Can not make changes nor manually enter "
                            "to Production state from another state different than Safe.")
        elif self.set_state != Node.DEBUG:
            raise ValidationError("Initial state must be Debug")
        # clean sliver_pub_ipv4 and _range
        if self.sliver_pub_ipv4 == Node.NONE:
            if self.sliver_pub_ipv4_range:
                msg = "Sliver pub IPv4 range must be empty when sliver pub IPv4 is none"
                raise ValidationError(msg)
        elif self.sliver_pub_ipv4 == Node.DHCP:
            validate_dhcp_range(self.sliver_pub_ipv4_range)
        elif self.sliver_pub_ipv4 == Node.RANGE:
            validate_ipv4_range(self.sliver_pub_ipv4_range)
        super(Node, self).clean()
    
    def update_set_state(self, commit=True):
        mgmtnet_conf = getattr(self.mgmt_net, 'is_configured', False)
        api_conf = getattr(self.api, 'is_configured', False)
        if not mgmtnet_conf or not api_conf:
            # bad_conf
            self.set_state = Node.DEBUG
        else:
            if self.set_state == Node.DEBUG:
                # transition to safe when all config is correct
                self.set_state = Node.SAFE
            elif self.set_state == Node.PRODUCTION:
                #TODO transition to SAFE if changes are detected
                #     self.set_state = Node.SAFE
                pass
        if commit:
            self.save(updated_set_state=True)
    
    def save(self, *args, **kwargs):
        updated_set_state = kwargs.pop('updated_set_state', False)
        super(Node, self).save(*args, **kwargs)
        # Call after save to be able to access related objects
        if not updated_set_state:
            self.update_set_state()
    
    @property
    def api(self):
        try:
            return self._api
        except NodeApi.DoesNotExist:
            return None
    
    @api.setter
    def api(self, value):
        if value is None:
            try:
                self._api.delete()
            except NodeApi.DoesNotExist:
                return  # is alreday None
        self._api = value
    
    def reboot(self):
        self.boot_sn += 1
        self.save()
    
    def get_sliver_mac_prefix(self):
        if self.sliver_mac_prefix: 
            return self.sliver_mac_prefix
        return SLIVER_MAC_PREFIX_DFLT
    
    def get_priv_ipv4_prefix(self):
        if self.priv_ipv4_prefix:
            return self.priv_ipv4_prefix
        return PRIV_IPV4_PREFIX_DFLT
    
    def get_priv_ipv6_prefix(self):
        return PRIV_IPV6_PREFIX
    
    @property
    def sliver_pub_ipv4_num(self):
        """
        Number of available IPv4 for slivers
        [BASE_IP]#N when sliver_pub_ipv4_range is not empty
        """
        if self.sliver_pub_ipv4_range:
            return int(self.sliver_pub_ipv4_range.split('#')[1])
        return 0
    
    def generate_certificate(self, key, commit=False, user=None):
        if user is None:
            # We pick one pseudo-random admin
            assert self.group.admins.exists()
            user = self.group.admins[0]
        if not key:
            # restore stored private key
            key = self.keys.private or self.keys.tinc
            assert key, 'A private key should be provided to generate a certificate.'
        addr = str(self.mgmt_net.addr)
        key = str(key)
        bob = Bob(key=key)
        scr = bob.create_request(Email=user.email, CN=addr)
        signed_cert = self.mgmt_net.sign_cert_request(scr)
        
        # Keep current certificate if node API has been customized
        # (e.g. API delegated to a gateway)
        if commit:
            if self.api is None:
                self.api = NodeApi.objects.create_default(node=self)
            
            # Check if node API base_uri refers node mgmt_net addr
            if url_on_mgmt_net(self.api.base_uri, self.mgmt_net.addr):
                self.api.cert = signed_cert
                self.api.save()
        
        return signed_cert


class BaseProp(models.Model):
    """Base model for node and sever properties"""
    name = models.CharField(max_length=32,
            help_text='Per node unique single line of free-form text with no '
                      'whitespace surrounding it.',
            validators=[validate_prop_name])
    value = models.CharField(max_length=256)
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return self.name


class NodeProp(BaseProp):
    """
    A mapping of (non-empty) arbitrary node property names to their (string)
    values.
    """
    node = models.ForeignKey(Node, related_name='properties')
    
    class Meta:
        unique_together = ('node', 'name')
        verbose_name = 'node property'
        verbose_name_plural = 'node properties'


class DirectIface(models.Model):
    """
    Interfaces used as direct interfaces.
    
    See node architecture: http://wiki.confine-project.eu/arch:node
    """
    name = models.CharField(max_length=16, validators=[validate_net_iface_name_with_vlan],
            help_text='The name of the interface used as a local interface (non-empty). '
                      'See <a href="https://wiki.confine-project.eu/arch:node">node '
                      'architecture</a>.')
    node = models.ForeignKey(Node, related_name='direct_ifaces')
    
    class Meta:
        unique_together = ['name', 'node']
        verbose_name = 'direct network interface'
        verbose_name_plural = 'direct network interfaces'
    
    def __unicode__(self):
        return self.name


class ServerQuerySet(models.query.QuerySet):
    def delete(self):
        """Check that at least one server remains undeleted."""
        if self.count() == self.model.objects.count():
            raise PermissionDenied("At least one server must exist!")
        super(ServerQuerySet, self).delete()


class ServerManager(models.Manager):
    def get_queryset(self):
        return ServerQuerySet(self.model, using=self.db)
    
    def get_default(self):
        if not self.exists():
            raise self.model.DoesNotExist
        return self.order_by('id').first()

class Server(models.Model):
    """
    Describes the testbed server (controller).
    """
    name = models.CharField(max_length=256, unique=True,
            help_text='A unique name for this server. A single non-empty line of '
                      'free-form text with no whitespace surrounding it.',
            validators=[validate_name])
    description = models.TextField(blank=True,
            help_text='Free-form textual description of this server.')
    
    objects = ServerManager()
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['pk']
    
    def delete(self):
        if Server.objects.count() == 1:
            raise PermissionDenied("At least one server must exist!")
        super(Server, self).delete()

class ServerProp(BaseProp):
    """
    A mapping of (non-empty) arbitrary server property names to their (string)
    values.
    """
    server = models.ForeignKey(Server, related_name='properties')
    
    class Meta:
        unique_together = ('server', 'name')
        verbose_name = 'server property'
        verbose_name_plural = 'server properties'


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
            validators=[validate_name])
    description = models.TextField(blank=True,
            help_text='Optional free-form textual description of this island.')
    
    def __unicode__(self):
        return self.name


###  Signals  ###

# update the node set_state on nodeapi update
def nodeapi_changed(sender, instance, **kwargs):
    # Do nothing while loading fixtures or running migrations
    if kwargs.get('raw', False):
        return
    instance.node.update_set_state()

post_save.connect(nodeapi_changed, sender=NodeApi)
post_delete.connect(nodeapi_changed, sender=NodeApi)

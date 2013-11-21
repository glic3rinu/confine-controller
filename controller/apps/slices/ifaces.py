from django.core.exceptions import ValidationError
from IPy import IP

from controller.settings import DEBUG_IPV6_PREFIX
from controller.utils.ip import int_to_hex_str, split_len
from nodes.models import Node

from .models import Sliver


class BaseIface(object):
    """
    Base class for defining Sliver Iface specific behaviour.
    """
    DEFAULT_NAME = 'eth0'
    ALLOW_BULK = True
    AUTO_CREATE = False
    CREATE_BY_DEFAULT = False
    UNIQUE = False
    
    def clean_model(self, iface):
        """ additional logic to be executed during model.clean() """
        if iface.parent:
            raise ValidationError("parent not allowed for this type of iface")
        if self.UNIQUE and iface.sliver_id:
            private_qs = type(iface).objects.filter(sliver=iface.sliver, type=iface.type)
            if iface.pk:
                private_qs = private_qs.exclude(pk=iface.pk)
            if private_qs.exists():
                raise ValidationError('There can only be one interface of type private')
    
    def ipv6_addr(self, iface):
        return None
    
    def ipv4_addr(self, iface):
        return None
    
    def is_allowed(self, slice, queryset):
        return True


class IsolatedIface(BaseIface):
    """
    Describes an Isolated interface of an sliver: It is used for sharing the
    same physical interface but isolated at L3, by means of tagging all the
    outgoing traffic with a VLAN tag per slice. By means of using an isolated
    interface, the researcher will be able to configure it at L3, but several
    slices may share the same physical interface.
    """
    DEFAULT_NAME = 'iso0'
    ALLOW_BULK = False
    
    def clean_model(self, iface):
        if iface.sliver_id and not iface.sliver.slice.vlan_nr:
            raise ValidationError("Slice vlan_nr is mandatory for isolated interfaces.")
        if not iface.parent:
            raise ValidationError("Parent is mandatory for isolated interfaces.")
    
    def is_allowed(self, slice, queryset):
        return bool(slice.vlan_nr)


class Pub4Iface(BaseIface):
    """
    Local network interface: assigned by DHCP or using a configuration range
    Describes an IPv4 Public Interface for an sliver. Traffic from a public
    interface will be bridged to the community network.
    """
    DEFAULT_NAME = 'pub0'
    
    def clean_model(self, iface):
        super(Pub4Iface, self).clean_model(iface)
        if iface.sliver_id and iface.sliver.node.sliver_pub_ipv4 == 'none':
            raise ValidationError("public4 is only available if node's sliver_pub_ipv4 is not None")
    
    def ipv4_addr(self, iface):
        return 'Unknown'


class Pub6Iface(BaseIface):
    """
    Local network interface: assigned by stateless autoconf or DHCPv6
    Describes an IPv6 Public Interface for an sliver. Traffic from a public
    interface will be bridged to the community network.
    """
    DEFAULT_NAME = 'pub1'
    
    def ipv6_addr(self, iface):
        return 'Unknown'
    
    def is_allowed(self, slice, queryset):
        return not queryset.filter(sliver_pub_ipv6=Node.NONE).exists()


class DebugIface(BaseIface):
    """
    Debug interface and address whose host side veth interface will be placed in
    the local bridge, thus allowing access to the debug network. The address is
    easily predictable and computed according to the address scheme, and no
    gateway is expected to exist in this network. This interface allows connections
    to other nodes and slivers in the same local network, which should be useful
    for debugging purposes
    """
    DEFAULT_NAME = 'dbg0'
    
    def ipv6_addr(self, iface):
        """ DEBUG_IPV6_PREFIX:N:10ii:ssss:ssss:ssss """
        # Hex representation of the needed values
        nr = '10' + int_to_hex_str(iface.nr, 2)
        node_id = int_to_hex_str(iface.sliver.node_id, 4)
        slice_id = int_to_hex_str(iface.sliver.slice_id, 12)
        ipv6_words = DEBUG_IPV6_PREFIX.split(':')[:3]
        ipv6_words.extend([node_id, nr])
        ipv6_words.extend(split_len(slice_id, 4))
        return IP(':'.join(ipv6_words))


class PrivateIface(BaseIface):
    """
    Describes a Private Interface of an sliver. Traffic from a private interface
    will be forwarded to the community network by means of NAT. Every sliver
    will have at least a private interface.
    """
    DEFAULT_NAME = 'priv'
    AUTO_CREATE = True
    UNIQUE = True
    
    def ipv6_addr(self, iface):
        """ PRIV_IPV6_PREFIX:0:1000:ssss:ssss:ssss/64 """
        # Hex representation of the needed values
        nr = '10' + int_to_hex_str(iface.nr, 2)
        slice_id = int_to_hex_str(iface.sliver.slice_id, 12)
        ipv6_words = iface.sliver.node.get_priv_ipv6_prefix().split(':')[:3]
        ipv6_words.extend(['0', nr])
        ipv6_words.extend(split_len(slice_id, 4))
        return IP(':'.join(ipv6_words))
    
    def ipv4_addr(self, iface):
        """ {X.Y.Z}.S is the address of sliver #S """
        return 'Unknown'
    
    def _get_nr(self, iface):
        return 0


Sliver.register_iface(Pub4Iface, 'public4')
Sliver.register_iface(IsolatedIface, 'isolated')
Sliver.register_iface(Pub6Iface, 'public6')
Sliver.register_iface(PrivateIface, 'private')
Sliver.register_iface(DebugIface, 'debug')

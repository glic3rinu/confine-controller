from django.core.exceptions import ValidationError
from IPy import IP

from common.ip import int_to_hex_str, split_len
from nodes.settings import NODES_DEBUG_IPV6_PREFIX

from .models import Sliver


class BaseIface(object):
    """
    Base class for defining Sliver Iface specific behaviour.
    Four methods are available for overriding:
        def clean(self, iface)
        def ipv6_addr(self, iface)
        def ipv4_addr(self, iface)
        def _get_nr(self, iface)
    """
    def clean(self, iface):
        if iface.parent:
            raise ValidationError("parent not allowed for this type of iface")
    
    def ipv6_addr(self, iface):
        return None
    
    def ipv4_addr(self, iface):
        return None


class IsolatedIface(BaseIface):
    """
    Describes an Isolated interface of an sliver: It is used for sharing the 
    same physical interface but isolated at L3, by means of tagging all the 
    outgoing traffic with a VLAN tag per slice. By means of using an isolated 
    interface, the researcher will be able to configure it at L3, but several 
    slices may share the same physical interface.
    """
    def clean(self, iface):
        if not iface.parent:
            raise ValidationError("parent is mandatory for isolated interfaces.")


class Pub6Iface(BaseIface):
    """
    Local network interface: assigned by stateless autoconf or DHCPv6
    Describes an IPv6 Public Interface for an sliver. Traffic from a public
    interface will be bridged to the community network.
    """
    def clean(self, iface):
        super(PubIface, self).clean(iface)
        if iface.sliver.nodesliver_pub_ipv4 == 'none':
            raise ValidationError("public4 is only available if node's sliver_pub_ipv4 is not None")
    
    def ipv6_addr(self, iface):
        return 'Unknown'


class Pub4Iface(BaseIface):
    """
    Local network interface: assigned by DHCP or using a configuration range
    Describes an IPv4 Public Interface for an sliver. Traffic from a public
    interface will be bridged to the community network.
    """
    def clean(self, iface):
        super(Pub4Iface, self).clean(iface)
        if iface.sliver.node.sliver_pub_ipv4 == 'none':
            raise ValidationError("public4 is only available if node's sliver_pub_ipv4 is not None")
    
    def ipv4_addr(self, iface):
        return 'Unknown'


class DebugIface(BaseIface):
    def ipv6_addr(self, iface):
        """ DEBUG_IPV6_PREFIX:N:10ii:ssss:ssss:ssss """
        # Hex representation of the needed values
        nr = '10' + int_to_hex_str(iface.nr, 2)
        node_id = int_to_hex_str(iface.sliver.node_id, 4)
        slice_id = int_to_hex_str(iface.sliver.slice_id, 12)
        
        ipv6_words = NODES_DEBUG_IPV6_PREFIX.split(':')[:3]
        ipv6_words.extend([node_id, nr])
        ipv6_words.extend(split_len(slice_id, 4))
        return IP(':'.join(ipv6_words))


class PrivateIface(BaseIface):
    """
    Describes a Private Interface of an sliver.Traffic from a private interface 
    will be forwarded to the community network by means of NAT. Every sliver 
    will have at least a private interface.
    """
    def clean(self, iface):
        super(PrivateIface, self).clean(iface)
        private_qs = iface.__class__.objects.filter(sliver=iface.sliver, type='private')
        if iface.pk:
            private_qs = private_qs.exclude(pk=iface.pk)
        if private_qs.exists():
            raise ValidationError('There can only be one interface of type private')
    
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
        prefix = iface.sliver.node.get_priv_ipv4_prefix()
        ipv4_words = prefix.split('.')[:3]
        ipv4_words.append('%d' % iface.sliver.nr)
        return IP('.'.join(ipv4_words))
    
    def _get_nr(self, iface):
        return 0


Sliver.register_iface(Pub4Iface, 'public4')
Sliver.register_iface(IsolatedIface, 'isolated')
Sliver.register_iface(Pub6Iface, 'public6')
Sliver.register_iface(PrivateIface, 'private')
Sliver.register_iface(DebugIface, 'debug')

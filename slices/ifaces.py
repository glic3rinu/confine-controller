from django.core.exceptions import ValidationError
from IPy import IP

from common.ip import int_to_hex_str, split_len

from .models import Sliver


class BaseIface(object):
    """
    Base class for defining Sliver Ifaces
    """
    def clean(self, iface):
        if iface.parent:
            raise ValidationError("parent not allowed for this type of iface")
    
    def ipv6_addr(self, iface):
        return None
    
    def ipv4_addr(self, iface):
        return None


class IsolatedIface(BaseIface):
    def clean(self, iface):
        if not iface.parent:
            raise ValidationError("Parent is mandatory for isolated interfaces.")


class Public6Iface(BaseIface):
    def clean(self, iface):
        if iface.sliver.nodesliver_pub_ipv4 is None:
            raise ValidationError("public4 is only available if node's sliver_pub_ipv4 is not None")


class Public4Iface(BaseIface):
    def clean(self, iface):
        if iface.sliver.node.sliver_pub_ipv4 is None:
            raise ValidationError("public4 is only available if node's sliver_pub_ipv4 is not None")
    
class DebugIface(BaseIface):
    def ipv6_addr(self, iface):
        """ DEBUG_IPV6_PREFIX:N:10ii:ssss:ssss:ssss """
        # Hex representation of the needed values
        nr = '10' + int_to_hex_str(iface.nr, 2)
        node_id = int_to_hex_str(iface.sliver.node_id, 4)
        slice_id = int_to_hex_str(iface.sliver.slice_id, 12)
        from nodes.settings import NODES_DEBUG_IPV6_PREFIX
        ipv6_words = NODES_DEBUG_IPV6_PREFIX.split(':')[:3]
        ipv6_words.extend([node_id, nr])
        ipv6_words.extend(split_len(slice_id, 4))
        return IP(':'.join(ipv6_words))


class PrivateIface(BaseIface):
    def clean(self, iface):
        private_qs = iface.__class__.objects.filter(sliver=iface.sliver, type='private')
        if iface.pk:
            private_qs = private_qs.exclude(pk=iface.pk)
        if private_qs.exists():
            raise ValidationError('There can only be one interface of type private')
    
    def ipv6_addr(self, iface):
        """ PRIV_IPV6_PREFIX:0:1000:ssss:ssss:ssss/64 """
        nr = '10' + int_to_hex_str(iface.nr, 2)
        slice_id = int_to_hex_str(iface.sliver.slice_id, 12)
        ipv6_words = iface.sliver.node.get_priv_ipv6_prefix().split(':')[:3]
        node_id = '0'
        ipv6_words.extend([node_id, nr])
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


Sliver.register_iface(Public4Iface, 'public4')
Sliver.register_iface(IsolatedIface, 'isolated')
Sliver.register_iface(Public6Iface, 'public6')
Sliver.register_iface(PrivateIface, 'private')
Sliver.register_iface(DebugIface, 'debug')

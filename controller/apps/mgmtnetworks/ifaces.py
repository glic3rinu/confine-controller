from django.core.exceptions import ValidationError
from IPy import IP

from controller.settings import MGMT_IPV6_PREFIX
from controller.utils.ip import int_to_hex_str, split_len
from slices.ifaces import BaseIface
from slices.models import Sliver


class MgmtIface(BaseIface):
    """
    Describes the management network interface for an sliver. This
    interface allows connections from the management network to the
    sliver and optional access to whatever other networks are routed by
    testbed gateways in the management network.
    
    """
    DEFAULT_NAME = 'mgmt0'
    UNIQUE = False
    CREATE_BY_DEFAULT = True
    NR_MAIN_IFACE = 1
    
    def clean_model(self, iface):
        super(MgmtIface, self).clean_model(iface)
        is_main_iface = (not hasattr(iface, 'sliver') or
                         not iface.sliver.interfaces.filter(type=iface.type)\
                                                    .exclude(id=iface.id).exists())
        if is_main_iface and iface.nr != MgmtIface.NR_MAIN_IFACE:
            raise ValidationError("nr should be %i for the main management "
                                  "interface." % MgmtIface.NR_MAIN_IFACE)
    
    def ipv6_addr(self, iface):
        """ MGMT_IPV6_PREFIX:N:10ii:ssss:ssss:ssss/64 """
        # Hex representation of the needed values
        nr = '10' + int_to_hex_str(iface.nr, 2)
        node_id = int_to_hex_str(iface.sliver.node_id, 4)
        slice_id = int_to_hex_str(iface.sliver.slice_id, 12)
        ipv6_words = MGMT_IPV6_PREFIX.split(':')[:3]
        ipv6_words.extend([node_id, nr])
        ipv6_words.extend(split_len(slice_id, 4))
        return IP(':'.join(ipv6_words))


Sliver.register_iface(MgmtIface, 'management')

from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address
from IPy import IP
from M2Crypto import X509

from users.models import Group


def validate_sliver_mac_prefix(value):
    # TODO also limit to 16 bits
    try: 
        int(value, 16)
    except: 
        raise ValidationError('%s is not a hex value.' % value)


def validate_ipv4_range(value):
    try: 
        ip, offset = value.split('#')
        validate_ipv4_address(ip)
        int(offset)
    except:
        raise ValidationError('Range %s has not a valid format (IPv4#N).' % value)


def validate_dhcp_range(value):
    try:
        offset = value.split('#')[1]
        int(offset)
    except:
        raise ValidationError('Range %s has not a valid format (#N).' % value)


def validate_scr(scr, node):
    try:
        scr = X509.load_request_string(str(scr))
    except:
        raise ValidationError('Not a valid SCR')
    
    subject = scr.get_subject()
    if node.mgmt_net.addr != IP(subject.CN):
        raise ValidationError("CN != node.mgmt_net.addr: %s != %s" % (subject.CN, node.mgmt_net.addr))
    
    if not Group.objects.filter(node=node, roles__user__email=subject.emailAddress, roles__is_admin=True).exists():
        raise ValidationError("No admin with '%s' email address for this node." % subject.emailAddress)


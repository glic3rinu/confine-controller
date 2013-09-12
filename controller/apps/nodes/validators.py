from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address
from IPy import IP
from M2Crypto import X509

from users.models import Group


def validate_sliver_mac_prefix(value):
    try: 
        int_value = int(value, 16)
    except:
        raise ValidationError('%s is not a correct hex value.' % value)
    # Check if fits in 16 bits
    if int_value > 65535:
        raise ValidationError('%s is not a 16-bit integer number in hex' % value)


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


def validate_csr(csr, node):
    """ Validate Certificate Signing Request (CSR) """
    try:
        csr = X509.load_request_string(str(csr))
    except:
        raise ValidationError('Not a valid CSR')
    
    subject = csr.get_subject()
    if not subject.CN or node.mgmt_net.addr != IP(subject.CN):
        raise ValidationError("Common Name (CN) must be equeal than the "\
            "node management address: %s != %s" % (subject.CN, node.mgmt_net.addr))
    
    if not Group.objects.filter(nodes=node, roles__user__email=subject.emailAddress, roles__is_admin=True).exists():
        raise ValidationError("No admin with '%s' email address for this node." % subject.emailAddress)


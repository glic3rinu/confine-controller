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


def validate_priv_ipv4_prefix(value):
    try:
        ip = IP(value)
    except:
        raise ValidationError('"%s" is not a IPv4/24 private network' % value)
    if ip.version() != 4 or ip.strNetmask() != '255.255.255.0' or ip.iptype() != 'PRIVATE':
        raise ValidationError('"%s" is not a IPv4/24 private network' % ip)


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
    if not subject.CN:
        raise ValidationError("Required subject Common Name (CN) not provided")
    try:
        cnip = IP(subject.CN)
    except ValueError:
        msg = "Subject Common Name (CN) '%s' is not a valid IP address"
        raise ValidationError(msg % subject.CN)
    if node.mgmt_net.addr != cnip:
        msg = "Common Name (CN) must be equeal to node management address: '%s' != '%s'"
        raise ValidationError(msg % (subject.CN, node.mgmt_net.addr))

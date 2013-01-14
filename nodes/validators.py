from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address

from M2Crypto import X509


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


def validate_scr(value):
    try: X509.load_cert_string(str(value))
    except: raise ValidationError('Not a valid SCR')
    # TODO validate node's RD management address (2001:db8:cafe::2) as a distinguished name and the technician's e-mail address for contact

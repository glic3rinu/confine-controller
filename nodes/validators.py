from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address


def validate_sliver_mac_prefix(value):
    # TODO also limit to 16 bits
    try: int(value, 16)
    except: ValidationError('%s is not a hex value.' % value)


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

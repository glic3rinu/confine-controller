from django.core.exceptions import ValidationError

from common.validators import Ipv4Validator


def SliverMacPrefixValidator(value):
    # TODO also limit to 16 bits
    try: int(value, 16)
    except: ValidationError('%s is not a hex value.' % value)


def Ipv4Range(value):
    try: 
        ip, offset = value.split('#')
        Ipv4Validator(ip)
        int(offset)
    except:
        raise ValidationError('%s has not a valid format (IPv4#N).' % value)



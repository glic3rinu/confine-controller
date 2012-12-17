import re
from uuid import UUID

from Crypto import PublicKey
from django.core import validators
from django.core.exceptions import ValidationError


def UUIDValidator(value):
    try: 
        UUID(value)
    except:
        raise ValidationError('%s is a badly formed hexadecimal UUID string.' % value)


def RSAPublicKeyValidator(value):
    try: 
        PublicKey.RSA.importKey(value)
    except:
        raise ValidationError('This is not a valid RSA public key.')


def NetIfaceNameValidator(value):
    validators.RegexValidator(re.compile('^[a-z]+[0-9]*$'),
                              'Enter a valid network interface name.', 'invalid')(value)


def Ipv4Validator(value):
    ValidIpAddressRegex = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
    validators.RegexValidator(re.compile(ValidIpAddressRegex),
                              'Insert a valid IPv4 address.', 'invalid')(value)


def HostNameValidator(value):
    ValidHostnameRegex = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
    validators.RegexValidator(re.compile(ValidHostnameRegex),
                              'Insert a valid host name.', 'invalid')(value)


def OrValidator(validators):
    """
    Run validators with an OR logic
    """
    def closure(value, validators=validators):
        msg = []
        for validator in validators:
            try: validator(value)
            except ValidationError, e: 
                msg.append(str(e))
            else: return
        raise type(e)(' OR '.join(msg))
    return closure

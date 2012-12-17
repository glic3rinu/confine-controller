import re
from uuid import UUID

from Crypto import PublicKey
from django.core import validators
from django.core.exceptions import ValidationError


def validate_uuid(value):
    try: 
        UUID(value)
    except:
        raise ValidationError('%s is a badly formed hexadecimal UUID string.' % value)


def validate_rsa_pubkey(value):
    try: 
        PublicKey.RSA.importKey(value)
    except:
        raise ValidationError('This is not a valid RSA public key.')


def validate_net_iface_name(value):
    validators.RegexValidator(re.compile('^[a-z]+[0-9]*$'),
                              'Enter a valid network interface name.', 'invalid')(value)


def validate_host_name(value):
    ValidHostnameRegex = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
    validators.RegexValidator(re.compile(ValidHostnameRegex),
                              'Insert a valid host name.', 'invalid')(value)


class OrValidator(object):
    """
    Run validators with an OR logic
    """
    def __init__(self, validators):
        self.validators = validators
    
    def __call__(self, value):
        msg = []
        print self.validators
        for validator in self.validators:
            try: validator(value)
            except ValidationError, e: 
                # TODO get exception message in a readable way not:
                #      [u'blabana'] or [u'kajkja'] ...
                msg.append(str(e))
            else: return
        raise type(e)(' OR '.join(msg))
        

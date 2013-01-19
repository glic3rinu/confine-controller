import re
from uuid import UUID

from django.core import validators
from django.core.exceptions import ValidationError
from M2Crypto import BIO, RSA

from common.ssl import pkcs_to_x501


def validate_uuid(value):
    try: 
        UUID(value)
    except:
        raise ValidationError('%s is a badly formed hexadecimal UUID string.' % value)


def validate_rsa_pubkey(value):
    """ Validate X.501 and PKCS#1 RSA public keys """
    value = value.encode('ascii')
    try:
        # ckeck X.501 formatted key
        bio = BIO.MemoryBuffer(value)
        RSA.load_pub_key_bio(bio)
    except:
        try:
            # Check PKCS#1 formatted key (tinc favourite format)
            pk = pkcs_to_x501(value)
            bio = BIO.MemoryBuffer(pk)
            RSA.load_pub_key_bio(bio)
        except:
            raise ValidationError('This is not a valid RSA (X.501 or PKCS#1) public key.')


def validate_net_iface_name(value):
    validators.RegexValidator(re.compile('^[a-z]+[0-9]*$'),
                              'Enter a valid network interface name.', 'invalid')(value)


def validate_host_name(value):
    ValidHostnameRegex = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
    validators.RegexValidator(re.compile(ValidHostnameRegex),
                              'Insert a valid host name.', 'invalid')(value)


def validate_prop_name(value):
    validators.RegexValidator(re.compile('^[a-z][_0-9a-z]*[0-9a-z]$'),
                              'Enter a valid property name.', 'invalid')(value)


def validate_ascii(value):
    try:
        value.decode('ascii')
    except UnicodeDecodeError:
        raise ValidationError('This is not an ASCII string.')


class OrValidator(object):
    """
    Run validators with an OR logic
    """
    def __init__(self, validators):
        self.validators = validators
    
    def __call__(self, value):
        msg = []
        for validator in self.validators:
            try: validator(value)
            except ValidationError, e: 
                # TODO get exception message in a readable way not:
                #      [u'blabana'] or [u'kajkja'] ....
                msg.append(str(e))
            else: return
        raise type(e)(' OR '.join(msg))
        

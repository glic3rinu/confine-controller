import re
from uuid import UUID

from django.core import validators
from django.core.exceptions import ValidationError
from M2Crypto import BIO, RSA


def validate_uuid(value):
    try: 
        UUID(value)
    except:
        raise ValidationError('%s is a badly formed hexadecimal UUID string.' % value)


def validate_rsa_pubkey(value):
    """ Validate X.501 and PKCS#1 RSA public keys """
    value = value.encode('ascii')
    bio = BIO.MemoryBuffer(value)
    try:
        # ckeck X.501 formatted key
        RSA.load_pub_key_bio(bio)
    except:
        # Check PKCS#1 formatted key (tinc favourite format), a bit hacky
        value = value.strip()
        try:
            # Convert from PKCS#1 to X.501
            # Tanks to Piet van Oostrum
            # https://groups.google.com/d/msg/comp.lang.python/1IP2p00diiY/htGAsHHFDTkJ
            pk = value.splitlines()
            assert pk[0] == '-----BEGIN RSA PUBLIC KEY-----'
            assert pk[-1] == '-----END RSA PUBLIC KEY-----'
            # Get rid of the 'RSA' in header and convert from PKCS#1 to X.501 trailer
            # Prepend X.501 header 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A' to the data
            pk = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A' + ''.join(pk[1:-1])
            # Reformat the lines to 64 characters
            pk = [pk[i:i+64] for i in range(0, len(pk), 64)]
            pk = '-----BEGIN PUBLIC KEY-----\n' + '\n'.join(pk) + '\n-----END PUBLIC KEY-----'
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
        

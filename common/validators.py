import re
from base64 import b64decode
from uuid import UUID

from Crypto.PublicKey import RSA as CryptoRSA
from Crypto.Util import asn1
from django.core import validators
from django.core.exceptions import ValidationError
from M2Crypto import BIO, RSA


def validate_uuid(value):
    try: 
        UUID(value)
    except:
        raise ValidationError('%s is a badly formed hexadecimal UUID string.' % value)


def validate_rsa_pubkey(value):
    # TODO use only M2Crypto ?
    # https://groups.google.com/d/topic/comp.lang.python/1IP2p00diiY/discussion
    bio = BIO.MemoryBuffer(value.encode('ascii'))
    try:
        # ckeck X.501 formatted key
        RSA.load_pub_key_bio(bio)
    except:
        # Check PKCS#1 formatted key (tinc favourite format), very hacky
        value = value.strip()
        seq = asn1.DerSequence()
        try:
            assert re.match('-----BEGIN.*PUBLIC KEY-----', value.splitlines()[0])
            assert re.match('-----END.*PUBLIC KEY-----', value.splitlines()[-1])
            key64 = '\n'.join(value.splitlines()[1:-1])
            keyDER = b64decode(key64)
            seq.decode(keyDER)
            CryptoRSA.construct((seq[0], seq[1]))
        except:
            raise ValidationError('This is not a valid RSA public key.')


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
        

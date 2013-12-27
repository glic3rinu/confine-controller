import base64
import re
import string
import struct
from uuid import UUID

from django.core import validators
from django.core.exceptions import ValidationError
from M2Crypto import BIO, RSA

from controller.utils.ssl import pkcs_to_x501


def validate_uuid(value):
    try: 
        UUID(value)
    except:
        msg = '%s is a badly formed hexadecimal UUID string.' % value
        raise ValidationError(msg)


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
            msg = 'This is not a valid RSA (X.501 or PKCS#1) public key.'
            raise ValidationError(msg)


def validate_ssh_pubkey(value):
    try:
        type, key_string, comment = value.split(None, 2) # maxsplit=2 allows comment containing spaces
        data = base64.decodestring(key_string)
        int_len = 4
        str_len = struct.unpack('>I', data[:int_len])[0] # this should return 7
        assert data[int_len:int_len+str_len] == type
    except:
        raise ValidationError('This is not a valid SSH public key.')


def validate_net_iface_name(value):
    validators.RegexValidator(re.compile('^[a-z]+[0-9]*$'),
            'Enter a valid network interface name.', 'invalid')(value)


def validate_host_name(value):
    ValidHostnameRegex = ("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)"
                          "*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
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

def validate_name(value):
    """
        A single non-empty line of free-form text with no whitespace
        surrounding it.
    """
    validators.RegexValidator('^\S.*\S$',
            'Enter a valid name.', 'invalid')(value)


def validate_sha256(value):
    """ SHA256 hex digest """
    if len(value) != 64 or not all(c in string.hexdigits for c in value):
        raise ValidationError('This is not an SHA256 HEX digest.')


def validate_file_extensions(extensions):
    def _validate_extensions(value, extensions=extensions):
        for extension in extensions:
            if value.name.endswith(extension):
                return
        msg = '"%s" does not have a valid extension %s' % (value, extensions)
        raise ValidationError(msg)
    return _validate_extensions


class OrValidator(object):
    """
    Run validators with an OR logic
    """
    def __init__(self, validators):
        self.validators = validators
    
    def __call__(self, value):
        msg = []
        for validator in self.validators:
            try:
                validator(value)
            except ValidationError, e:
                # TODO get exception message in a readable way not:
                #      [u'blabana'] or [u'kajkja'] ....
                msg.append(str(e))
            else:
                return
        raise type(e)(' OR '.join(msg))



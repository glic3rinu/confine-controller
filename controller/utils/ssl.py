from __future__ import absolute_import

import base64

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager


class SSLAdapter(HTTPAdapter):
    """
    An HTTPS Transport Adapter that uses an arbitrary SSL version.
    
    Thanks to Cory (Lukasa)
    https://lukasa.co.uk/2013/01/Choosing_SSL_Version_In_Requests/
    """
    def __init__(self, ssl_version=None, **kwargs):
        self.ssl_version = ssl_version
        super(SSLAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=self.ssl_version)


def _der_length(length):
    """ DER encoding of a length """
    if length < 128:
        return chr(length)
    prefix = 0x80
    result = ''
    while length > 0:
        result = chr(length & 0xff) + result
        length >>= 8
        prefix += 1
    return chr(prefix) + result


def pkcs_to_x501(pubkey):
    """ 
    Converts an RSA public key in PKCS#1 to X.501
    
    Thanks to Piet van Oostrum
    https://groups.google.com/d/msg/comp.lang.python/1IP2p00diiY/htGAsHHFDTkJ
    """
    pubkey = pubkey.strip()
    pk = pubkey.splitlines()
    assert pk[0] == '-----BEGIN RSA PUBLIC KEY-----', 'Wrong PKCS#1 header'
    assert pk[-1] == '-----END RSA PUBLIC KEY-----', 'Wrong PKCS#1 footer'
    pk = '\0' + base64.decodestring(''.join(pk[1:-1]))
    header = '\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01\x05\x00\x03'
    pk = header + _der_length(len(pk)) + pk
    pk = '\x30' + _der_length(len(pk)) + pk
    pk = '-----BEGIN PUBLIC KEY-----\n' + base64.encodestring(pk) + '-----END PUBLIC KEY-----'
    return pk

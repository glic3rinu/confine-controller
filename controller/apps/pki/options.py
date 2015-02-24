import time
import random
import sys
import os
import pwd
from base64 import b64encode

from M2Crypto import RSA, X509, EVP, ASN1, BIO

from controller.utils.paths import get_site_root

from . import settings


class CA(object):
    @property
    def priv_key_path(self):
        return settings.PKI_CA_PRIV_KEY_PATH % { 'site_root': get_site_root() }
    
    @property
    def pub_key_path(self):
        return settings.PKI_CA_PUB_KEY_PATH % { 'site_root': get_site_root() }
    
    @property
    def cert_path(self):
        return settings.PKI_CA_CERT_PATH % { 'site_root': get_site_root() }
    
    @property
    def cert_exp_days(self):
        return settings.PKI_CA_CERT_EXP_DAYS
    
    def get_key(self):
        return RSA.load_key(self.priv_key_path)
        # FIXME
#        return getattr(self, 'key', RSA.load_key(self.priv_key_path))
    
    def gen_key(self, commit=False):
        bob = Bob()
        key = bob.gen_key()
        # FIXME segfault here
#        self.key = bob.gen_key()
#        self.key.as_pem(cipher=None)
        if commit:
            bob.store_key(self.priv_key_path)
            bob.store_pub_key(self.pub_key_path)
        return key
    
    def get_cert(self):
        return X509.load_cert(self.cert_path)
    
    def gen_cert(self, **kwargs):
        commit = kwargs.pop('commit', False)
        bob = Bob(key=self.get_key())
        request = bob.create_request(**kwargs)
        cert = self.sign_request(request, ca=True)
        if commit:
            cert.save_pem(self.cert_path)
        return cert
    
    def sign_request(self, request, ca=False):
        if not isinstance(request, X509.Request):
            request = X509.load_request_string(str(request))
        ca_priv_evp = EVP.PKey()
        ca_priv_evp.assign_rsa(self.get_key())
        cert = X509.X509()
        # X509 version field is 0-based
        cert.set_version(0x2) # set to X509v3
        # Set Serial number
        serial = random.randrange(1, sys.maxint)
        cert.set_serial_number(serial)
        # Set Cert validity time
        cur_time = ASN1.ASN1_UTCTIME()
        cur_time.set_time(int(time.time()))
        expire_time = ASN1.ASN1_UTCTIME()
        expire_time.set_time(int(time.time()) + self.cert_exp_days*24*60*60)
        cert.set_not_before(cur_time)
        cert.set_not_after(expire_time)
        
        if ca:
            cert.set_issuer_name(request.get_subject())
            cert.add_ext(X509.new_extension('basicConstraints', 'CA:TRUE'))
        else:
            ca_cert = self.get_cert()
            cert.set_issuer_name(ca_cert.get_subject())
        
        cert.set_subject(request.get_subject())
        cert.set_pubkey(request.get_pubkey())
        cert.sign(ca_priv_evp, md="sha256")
        return cert


ca = CA()


class Bob(object):
    def __init__(self, key=None):
        if key is not None:
            self.load_key(key)
    
    def load_key(self, key):
        # Key can be a file, an string or an RSA object
        if not isinstance(key, RSA.RSA):
            try:
                key = RSA.load_key(key)
            except:
                key = RSA.load_key_string(key)
        self.key = key
        self.pkey = EVP.PKey()
        self.pkey.assign_rsa(key)
    
    def gen_key(self, path=None):
        new_key = RSA.gen_key(2048, 65537)
        self.load_key(new_key)
        if path is not None:
            self.store_key(path)
        return new_key
    
    def store_key(self, path):
        self.key.save_pem(path, cipher=None)
    
    def store_pub_key(self, path):
        self.key.save_pub_key(path)
    
    def get_key(self, format='X.501'):
        if format == 'X.501':
            mem = BIO.MemoryBuffer()
            self.key.save_key_bio(mem, cipher=None)
            return mem.getvalue()
        raise self.FormatError('format "%s" not supported' % format)
    
    def get_pub_key(self, format='X.501'):
        if format == 'OpenSSH':
            b64key = b64encode('\x00\x00\x00\x07ssh-rsa%s%s' % (self.key.e, self.key.n))
            username = pwd.getpwuid(os.getuid())[0] 
            # used to be os.getlogin(), not a good idea 
            # also see http://docs.python.org/2/library/os.html#os.getlogin
            
            hostname = os.uname()[1]
            return 'ssh-rsa %s %s@%s' % (b64key, username, hostname)
        if format == 'X.501':
            mem = BIO.MemoryBuffer()
            self.key.save_pub_key_bio(mem)
            return mem.getvalue()
        raise self.FormatError('format "%s" not supported' % format)
    
    def create_request(self, **subject):
        request = X509.Request()
        subject_name = X509.X509_Name()
        for key, value in subject.iteritems():
            setattr(subject_name, key, value)
        request.set_subject(subject_name)
        request.set_pubkey(pkey=self.pkey)
        request.sign(self.pkey, md="sha256")
        return request
    
    class FormatError(Exception): pass

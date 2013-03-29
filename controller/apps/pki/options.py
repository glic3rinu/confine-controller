import time, sys, random

from M2Crypto import RSA, X509, EVP, ASN1

from controller.utils.system import run
from controller.utils.paths import abs_or_reltosite

from . import settings


class CA(object):
    @property
    def priv_key_path(self):
        return abs_or_reltosite(settings.PKI_CA_PRIV_KEY_PATH)
    
    @property
    def pub_key_path(self):
        return abs_or_reltosite(settings.PKI_CA_PUB_KEY_PATH)
    
    @property
    def cert_path(self):
        return abs_or_reltosite(settings.PKI_CA_CERT_PATH)
    
    @property
    def cert_exp_days(self):
        return settings.PKI_CA_CERT_EXP_DAYS
    
    def get_key(self):
        try:
            return RSA.load_key(self.priv_key_path)
        except:
            return None
    
    def gen_key(self, commit=False):
        key = RSA.gen_key(2048, 65537)
        if commit:
            key.save_pem(self.priv_key_path, cipher=None)
            key.save_pub_key(self.pub_key_path)
        return key
    
    def get_cert(self):
        try:
            return X509.load_cert(self.cert_path)
        except:
            return None
    
    def gen_cert(self, **kwargs):
        commit = kwargs.pop('commit', False)
        bob = Bob(self.get_key())
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
        cert.set_version(3)
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
    def __init__(self, key):
        # we allow key to be a file, an string or a RSA object
        if not isinstance(key, RSA.RSA):
            try:
                key = RSA.load_key(key)
            except:
                key = RSA.load_key_string(key)
        self.pkey = EVP.PKey()
        self.pkey.assign_rsa(key)
    
    def create_request(self, **subject):
        request = X509.Request()
        subject_name = X509.X509_Name()
        for key, value in subject.iteritems():
            setattr(subject_name, key, value)
        request.set_subject(subject_name)
        request.set_pubkey(pkey=self.pkey)
        request.sign(self.pkey, md="sha256")
        return request

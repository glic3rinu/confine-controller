from M2Crypto import BIO, ASN1, RSA, X509, EVP

from .settings import CERT_PRIVATE_KEY_PATH, CERT_EXPIRATION

def sign_cert_request(scr):
    privkey = os.path.join(CERT_PRIVATE_KEY_PATH)
    privkey = EVP.load_key(privkey)
    request = X509.load_cert_string(str(cert_request))
    request.sign(privkey, md="sha256")
    return request.as_pem()


def generate_certificate(key, **subject):
    # we allow key to be a file and also an string
    try:
        key = RSA.load_key(key)
    except:
        key = RSA.load_key_string(key)
    pkey = EVP.PKey()
    pkey.assign_rsa(key)
    
    # time for certificate to stay valid
    cur_time = ASN1.ASN1_UTCTIME()
    cur_time.set_time(int(time.time()))
    expire_time = ASN1.ASN1_UTCTIME()
    # Expire certs in 4 years
    expire_time.set_time(int(time.time()) + CERT_EXPIRATION)
    # creating a certificate
    cert = X509.X509()
    cert.set_pubkey(pkey)
    subject_name = X509.X509_Name()
    for key, value in subject.iteritems():
        setattr(subject_name, key, value)
    cert.set_subject(subject_name)
    # TODO issuer info (confine)
    cert.set_issuer_name(subject_name)
    cert.set_not_before(cur_time)
    cert.set_not_after(expire_time)
    # self signing a certificate
    cert.sign(pkey, md="sha256")
    return cert.as_pem()

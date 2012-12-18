from django.core.management.base import BaseCommand
import M2Crypto, time, os


# TODO rename to 'create_ca' ?

class Command(BaseCommand):
    """
    Creates the certificate needed for the nodes to autenticate the server.
    """
    
    help = 'Creates the certificate needed for the nodes to autenticate the server'
    
    def handle(self, *args, **options):
        import nodes.settings
        
        # TODO allow user input, and use settings only as a defaults
        
        # Generating a Random RSA key pair (public and private):
        key = M2Crypto.RSA.gen_key(2048, 65537)
        
        # Saving the generated public and private key:
        # None is a specified password for testing purposes there is none
        key.save_key(os.path.join(settings.CERT_PATH, 'confine-private.pem'), None)
        key.save_pub_key(os.path.join(settings.CERT_PATH, 'confine-public.pem'))
        
        # Converting the RSA key into a PKey() which is stored in a certificate:
        pkey = M2Crypto.EVP.PKey()
        pkey.assign_rsa(key)
        
        # time for certificate to stay valid
        cur_time = M2Crypto.ASN1.ASN1_UTCTIME()
        cur_time.set_time(int(time.time()))
        expire_time = M2Crypto.ASN1.ASN1_UTCTIME()
        # Expire certs in 4 years
        expire_time.set_time(int(time.time()) + settings.CERT_EXPIRATION)
        # creating a certificate
        cert = M2Crypto.X509.X509()
        cert.set_pubkey(pkey)
        cs_name = M2Crypto.X509.X509_Name()
        cs_name.C = settings.CERT_C
        cs_name.CN = settings.CERT_CN
        cs_name.Email = settings.CERT_EMAIL
        cert.set_subject(cs_name)
        cert.set_issuer_name(cs_name)
        cert.set_not_before(cur_time)
        cert.set_not_after(expire_time)
        # self signing a certificate
        cert.sign(pkey, md="sha256")
        # save
        cert.save_pem(os.path.join(settings.CERT_PATH, 'cert'))
        
        return cert

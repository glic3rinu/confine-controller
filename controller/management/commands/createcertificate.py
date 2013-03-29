from django.core.management.base import BaseCommand
from M2Crypto import RSA, X509

from controller import settings
from controller.utils.system import run


# TODO rename to createca or setupca
# createrootcertificate ? 
# http://www.freebsdmadeeasy.com/tutorials/freebsd/create-a-ca-with-openssl.php

# TODO create a CA/PKI application which handles of these things? and revokes...
# https://github.com/dkerwin/django-pki

class Command(BaseCommand):
    help = 'Creates an RSA key and the testbed CA (root) certificate'
    
    def handle(self, *args, **options):
        gen_cert = False
        force_gen_cert = False # TODO
        # get or create private key
        try:
            RSA.load_key(settings.CA_PRIV_KEY_PATH)
        except:
            # generate a new key
            key = RSA.gen_key(1024, 65537)
            key.save_pem(settings.CA_PRIV_KEY_PATH, cipher=None)
            key.save_pub_key(settings.CA_PUB_KEY_PATH)
            gen_cert = True
        else:
            try:
                X509.load_cert(settings.CA_CERT_PATH)
            except:
                gen_cert = True
        
        if not force_gen_cert and not gen_cert:
            self.stdout.write('\nYour cert and keys are already in place.\n'
                              ' Use --force_gen_cert in order to overide them.\n\n')
            return
        
        if gen_cert:
            context = {
                'priv_key': settings.CA_PRIV_KEY_PATH,
                'cert': settings.CA_CERT_PATH,
                'days': settings.CA_CERT_EXP_DAYS,}
            # generate root certificate
            run('openssl req -new -x509 -key %(priv_key)s -out %(cert)s -days %(days)d' % context)

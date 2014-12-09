from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.six.moves import input

from pki import ca


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--override', dest='override', action='store_true',
                default=False, help='Force override cert and keys if exists.'),
            make_option('--country', dest='dn_country', default='',
                help='Certificate Distinguished Name Country.'),
            make_option('--state', dest='dn_state', default='',
                help='Certificate Distinguished Name STATE.'),
            make_option('--locality', dest='dn_locality', default='',
                help='Certificate Distinguished Name Country.'),
            make_option('--org_name', dest='dn_org_name', default='',
                help='Certificate Distinguished Name Organization Name.'),
            make_option('--org_unit', dest='dn_org_unit', default='',
                help='Certificate Distinguished Name Organization Unity.'),
            make_option('--email', dest='dn_email', default='',
                help='Certificate Distinguished Name Email Address.'),
            make_option('--common_name', dest='dn_common_name', default=None,
                help='Certificate Distinguished Name Common Name.'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '),
            )
    
    option_list = BaseCommand.option_list
    help = 'Creates an RSA key and the testbed CA (root) certificate'
    
    def handle(self, *args, **options):
        # TODO correct key file permissions
        override = options.get('override')
        interactive = options.get('interactive')
        
        try:
            key = ca.get_key()
        except IOError:
            key = False
        
        if override or not key:
            self.stdout.write('writing new private key to \'%s\'' % ca.priv_key_path)
            self.stdout.write('writing new public key to \'%s\'' % ca.pub_key_path)
            ca.gen_key(commit=True)
            override = True
        
        try:
            ca.get_cert()
        except IOError:
            override = True
        
        if override or not ca.get_cert():
            # Avoid import errors
            from nodes.models import Server
            server = Server.objects.first()
            common_name = options.get('common_name') or str(server.mgmt_net.addr)
            country = options.get('dn_country')
            state = options.get('dn_state')
            locality = options.get('dn_locality')
            org_name = options.get('dn_org_name')
            org_unit = options.get('dn_org_unit')
            email = options.get('dn_email')
            
            if interactive:
                msg = ('-----\n'
                    'You are about to be asked to enter information that\n'
                    'will be incorporated\n'
                    'into your certificate request.\n'
                    'What you are about to enter is what is called a\n'
                    'Distinguished Name or a DN.\n'
                    'There are quite a few fields but you can leave some blank\n'
                    '-----\n')
                self.stdout.write(msg)
                
                msg = 'Country Name (2 letter code) [%s]: ' % country
                country = input(msg) or country
                
                msg = 'State or Province Name (full name) [%s]: ' % state
                state = input(msg) or state
                
                msg = 'Locality Name (eg, city) [%s]: ' % locality
                locality = input(msg) or locality
                
                msg = 'Organization Name (eg, company) [%s]: ' % org_name
                org_name = input(msg) or org_name
                
                msg = 'Organizational Unit Name (eg, section) [%s]: ' % org_unit
                org_unit = input(msg) or org_unit
                
                msg = 'Email Address [%s]: ' % email
                email = input(msg) or email
            
            self.stdout.write('Common Name: %s' % common_name)
            subject = {
                'C': country,
                'S': state,
                'L': locality,
                'O': org_name,
                'OU': org_unit,
                'Email': email,
                'CN': common_name }
            cert = ca.gen_cert(commit=True, **subject)
            self.stdout.write('writing new certificate to \'%s\'' % ca.cert_path)
            
            # Update mgmt network Server APIs certificate
            server.api.filter(base_uri__contains=server.mgmt_net.addr).update(
                cert=cert.as_pem())
            return
        
        self.stdout.write('\nYour cert and keys are already in place.\n'
                          ' Use --override in order to override them.\n\n')

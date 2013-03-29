from optparse import make_option

from django.core.management.base import BaseCommand

from pki import ca, settings


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--overide', dest='overide', action='store_true',
                default=False, help='Force overide cert and keys if exists.'),
            make_option('--country', dest='dn_country',
                default=settings.PKI_DN_COUNTRY_DFLT,
                help='Certificate Distinguished Name Country.'),
            make_option('--state', dest='dn_state',
                default=settings.PKI_DN_STATE_DFLT,
                help='Certificate Distinguished Name STATE.'),
            make_option('--locality', dest='dn_locality',
                default=settings.PKI_DN_LOCALITY_DFLT,
                help='Certificate Distinguished Name Country.'),
            make_option('--org_name', dest='dn_org_name',
                default=settings.PKI_DN_ORG_NAME_DFLT,
                help='Certificate Distinguished Name Organization Name.'),
            make_option('--org_unit', dest='dn_org_unit',
                default=settings.PKI_DN_ORG_UNIT_DFLT,
                help='Certificate Distinguished Name Organization Unity.'),
            make_option('--email', dest='dn_email', default='',
                help='Certificate Distinguished Name Email Address.'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '
                     'You must use --username with --noinput, and must contain the '
                     'cleeryd process owner, which is the user how will perform tincd updates'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Creates an RSA key and the testbed CA (root) certificate'
    
    def handle(self, *args, **options):
        overide = options.get('overide')
        interactive = options.get('interactive')
        
        if overide or not ca.get_key():
            ca.gen_key(commit=True)
            self.stdout.write('writing new private key to \'%s\'' % ca.priv_key_path)
            self.stdout.write('writing new public key to \'%s\'' % ca.pub_key_path)
            overide = True
        
        if overide or not ca.get_cert():
            # TODO only if interactive
            msg = ('-----\n'
                'You are about to be asked to enter information that\n'
                'will be incorporated\n'
                'into your certificate request.\n'
                'What you are about to enter is what is called a\n'
                'Distinguished Name or a DN.\n'
                'There are quite a few fields but you can leave some blank\n'
                'For some fields there will be a default value,\n'
                'If you enter \'.\', the field will be left blank.\n'
                '-----\n')
            self.stdout.write(msg)
            country = options.get('dn_country')
            state = options.get('dn_state')
            locality = options.get('dn_locality')
            org_name = options.get('dn_org_name')
            org_unit = options.get('dn_org_unit')
            email = options.get('dn_email')
            
            if interactive:
                msg = 'Country Name (2 letter code) [%s]: ' % country
                country = raw_input(msg) or country
                
                msg = 'State or Province Name (full name) [%s]: ' % state
                state = raw_input(msg) or state
                
                msg = 'Locality Name (eg, city) [%s]: ' % locality
                locality = raw_input(msg) or locality
                
                msg = 'Organization Name (eg, company) [%s]: ' % org_name
                org_name = raw_input(msg) or org_name
                
                msg = 'Organizational Unit Name (eg, section) [%s]: ' % org_name
                org_unit = raw_input(msg) or org_unit
                
                msg = 'Email Address [%s]: ' % email
                email = raw_input(msg) or email
            
            # Avoid import errors
            from mgmtnetworks.tinc.models import TincServer
            common_name = str(TincServer.objects.get().address)
            self.stdout.write('Common Name: %s' % common_name)
            subject = {
                'C': country,
                'S': state,
                'L': locality,
                'O': org_name,
                'OU': org_unit,
                'Email': email,
                'CN': common_name }
            ca.gen_cert(commit=True, **subject)
            self.stdout.write('writing new certificate to \'%s\'' % ca.cert_path)
            return
        
        self.stdout.write('\nYour cert and keys are already in place.\n'
                          ' Use --overide in order to overide them.\n\n')

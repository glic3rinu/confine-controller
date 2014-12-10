from optparse import make_option

from django.core.management.base import BaseCommand

from pki import Bob

from maintenance.settings import MAINTENANCE_KEY_PATH, MAINTENANCE_PUB_KEY_PATH


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--override', dest='override', action='store_true',
                default=False, help='Force override cert and keys if exists.'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '),
            )
    
    option_list = BaseCommand.option_list
    help = 'Creates an RSA key for driving maintenance operations'
    
    def handle(self, *args, **options):
        # TODO correct key file permissions
        override = options.get('override')
        
        bob = Bob()
        
        key_path = MAINTENANCE_KEY_PATH
        pub_key_path = MAINTENANCE_PUB_KEY_PATH
        
        try:
            bob.load_key(key_path)
        except:
            override = True
        
        if override:
            bob.gen_key()
            self.stdout.write('Writing new key to \'%s\'' % MAINTENANCE_KEY_PATH)
            bob.store_key(MAINTENANCE_KEY_PATH)
            self.stdout.write('Writing new public key to \'%s\'' % MAINTENANCE_PUB_KEY_PATH)
            with open(MAINTENANCE_PUB_KEY_PATH, 'w+') as pub_key_path:
                pub_key_path.write(bob.get_pub_key(format='OpenSSH'))
            return

        self.stdout.write('\nYour keys are already in place.\n'
                          ' Use --override in order to override them.\n\n')

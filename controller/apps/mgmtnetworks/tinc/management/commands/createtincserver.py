import getpass, pwd, re, os
from optparse import make_option

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from common.system import check_root, run, get_default_celeryd_username
from nodes.models import Server


class Command(BaseCommand):
    """
    Creates the tincd config files and Server.tinc object.
    
    This method must be called by a superuser
    """
    
    def __init__(self, *args, **kwargs):
        # Options are defined in an __init__ method to support swapping out
        # custom user models in tests.
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--username', dest='username', default=get_default_celeryd_username(),
                help='Specifies the login for the superuser.'),
            make_option('--safe', dest='safe', action='store_true', default=False,
                help='Specifies if this command should regenerate the existing server '
                     'keys, if they exists. Useful combined with --noinput'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '
                     'You must use --username with --noinput, and must contain the '
                     'cleeryd process owner, which is the user how will perform tincd updates'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Creates the tincd config files and Server.tinc object'
    
    @transaction.commit_on_success
    @check_root
    def handle(self, *args, **options):
        from mgmtnetworks.tinc.models import TincServer
        from mgmtnetworks.tinc.settings import TINC_NET_NAME, TINC_MGMT_IPV6_PREFIX
        
        interactive = options.get('interactive')
        if not interactive:
            username = options.get('username')
            if not username:
                raise CommandError("You must use --username with --noinput.")
            # validate username
            try:
                username = pwd.getpwnam(username).pw_name
            except KeyError:
                raise CommandError("Username doesn't exists.")
        
        server = Server.objects.get_or_create(id=1)
        tinc_server = TincServer.objects.filter(object_id=1, content_type__model='server',
                                                content_type__app_label='nodes')
        
        safe = options.get('safe')
        protect = safe and tinc_server.exists()
        if tinc_server.exists():
            if interactive:
                msg = ("\nSeems that you already have a tinc server configured.\nThis will "
                       "generate a new tinc public key and delete all the configuration under "
                       "/etc/tinc/%s.\nDo you want to continue? (yes/no): " % TINC_NET_NAME)
                confirm = raw_input(msg)
                while 1:
                    if confirm == 'no':
                        return
                    if confirm == 'yes':
                        break
                    confirm = raw_input('Please enter either "yes" or "no": ')
            tinc_server = tinc_server[0]
        elif not safe:
            server_ct = ContentType.objects.get_for_model(Server)
            tinc_server = TincServer.objects.create(object_id=1, content_type=server_ct)
        
        if not protect:
            FILE_PATH = os.path.dirname(os.path.realpath(__file__))
            SCRIPT_PATH = os.path.abspath(os.path.join(FILE_PATH, '../../scripts/create_server.sh'))
            run("%s %s %s" % (SCRIPT_PATH, TINC_NET_NAME, TINC_MGMT_IPV6_PREFIX.split('::')[0]))
            
            # Get created pubkey
            pubkey = ''
            for line in file('/etc/tinc/%s/hosts/server' % TINC_NET_NAME):
                pubkey += line
                if line == '-----BEGIN RSA PUBLIC KEY-----\n':
                    pubkey = line
                elif line == '-----END RSA PUBLIC KEY-----\n':
                    break
        
        # Prompt for username/password, and any other required fields.
        # Enclose this whole thing in a try/except to trap for a
        # keyboard interrupt and exit gracefully.
        default_username = get_default_celeryd_username()
        username = None
        while username is None and interactive:
            if not username:
                input_msg = "Celeryd username"
                if default_username:
                    input_msg += " (leave blank to use '%s')" % default_username
                raw_value = raw_input(input_msg + ': ')
            if default_username and raw_value == '':
                raw_value = default_username
            # validate username
            try:
                username = pwd.getpwnam(raw_value).pw_name
            except KeyError:
                self.stderr.write("Error: %s" % '; '.join(e.messages))
                username = None
                continue
        
        if username is None:
            username = default_username
        
        if not protect:
            tinc_server.pubkey = pubkey
            tinc_server.save()
        run("""chown %(user)s /etc/tinc/%(net)s/hosts;
                 chmod +x /etc/tinc/%(net)s/tinc-up;
                 chmod +x /etc/tinc/%(net)s/tinc-down""" % {'net': TINC_NET_NAME,
                                                             'user': username})
        self.stdout.write('Tincd server successfully created and configured.')
        self.stdout.write(' * You may want to start it: /etc/init.d/tinc restart')

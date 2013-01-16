import getpass, pwd, re
from optparse import make_option
from subprocess import Popen, PIPE

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from nodes.models import Server


def get_default_celeryd_username():
    """ Introspect celeryd defaults file in order to get default celeryd username """
    user = None
    try: 
        celeryd_defaults = open('/etc/default/celeryd')
    except IOError: pass
    else:
        for line in celeryd_defaults.readlines():
            if 'CELERYD_USER=' in line:
                user = re.findall('"([^"]*)"', line)[0]
    return user


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
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '
                     'You must use --username with --noinput, and must contain the '
                     'cleeryd process owner, which is the user how will perform tincd updates'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Creates the tincd config files and Server.tinc object'
    
    @transaction.commit_on_success
    def handle(self, *args, **options):
        from tinc.models import TincServer
        from tinc.settings import TINC_NET_NAME, MGMT_IPV6_PREFIX
        
        if getpass.getuser() != 'root':
            raise CommandError('Sorry, create_tinc_server must be executed as a superuser (root)')
        
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
        if tinc_server.exists():
            if interactive:
                msg = ("\nSeems that you already have a tinc server configured.\nThis will "
                       "generate a new tinc public key and delete all the configuration under "
                       "/etc/tinc/%s.\nDo you want to continue? (yes/no): " % TINC_NET_NAME)
                confirm = raw_input(msg)
                while 1:
                    if confirm == 'no': return
                    if confirm == 'yes': break
                    confirm = raw_input('Please enter either "yes" or "no": ')
            tinc_server = tinc_server[0]
        else:
            tinc_server = TincServer.objects.create(object_id=1, 
                                                    content_type__model='server',
                                                    content_type__app_label='nodes')
        
        cmd = "tinc/scripts/create_server.sh %s %s" % (TINC_NET_NAME, 
                                                       MGMT_IPV6_PREFIX.split('::')[0])
        cmd = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = cmd.communicate()
        if cmd.returncode > 0:
            raise CreateTincdError(stderr)
        
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
        
        tinc_server.pubkey = pubkey
        tinc_server.save()
        cmd = """chown %(user)s /etc/tinc/%(net)s/hosts;
                 chmod o+x /etc/tinc/%(net)s/tinc-{up,down}""" % {'net': TINC_NET_NAME, 
                                                                  'user': username}
        cmd = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = cmd.communicate()
        if cmd.returncode > 0:
            raise self.CreateTincdError(stderr)
        self.stdout.write('Tincd server successfully created and configured.')
        self.stdout.write(' * You may want to start it: /etc/init.d/tinc restart')
    
    class CreateTincdError(Exception): pass

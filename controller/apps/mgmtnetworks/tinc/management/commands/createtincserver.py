import getpass, pwd, re, os, functools
from optparse import make_option

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from controller.utils import update_settings
from controller.utils.system import check_root, run, get_default_celeryd_username
from nodes.models import Server


class Command(BaseCommand):
    """
    Creates the tincd config files and Server.tinc object.
    
    This method must be called by a superuser
    """
    
    def __init__(self, *args, **kwargs):
        # Options are defined in an __init__ method to support swapping out
        # custom user models in tests.
        from mgmtnetworks.tinc.settings import TINC_MGMT_IPV6_PREFIX, TINC_PORT_DFLT
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--username', dest='username', default=get_default_celeryd_username(),
                help='Specifies the login for the superuser.'),
            make_option('--mgmt_prefix', dest='mgmt_prefix', default=TINC_MGMT_IPV6_PREFIX,
                help='Mgmt prefix, the settings file will be updated.'),
            make_option('--tinc_port_dflt', dest='tinc_port_dflt', default=TINC_PORT_DFLT,
                help='Tinc port default, the settings file will be updated.'),
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
        from mgmtnetworks.tinc.settings import TINC_NET_NAME, TINC_MGMT_IPV6_PREFIX, TINC_PORT_DFLT
        
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
        
        server, created = Server.objects.get_or_create(id=1)
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
                        protect = False
                        break
                    confirm = raw_input('Please enter either "yes" or "no": ')
            tinc_server = tinc_server[0]
        else:
            server_ct = ContentType.objects.get_for_model(Server)
            tinc_server = TincServer.objects.create(object_id=1, content_type=server_ct)
        
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
        
        tinc_port = options.get('tinc_port_dflt')
        mgmt_prefix = options.get('mgmt_prefix')
        update_settings(TINC_MGMT_IPV6_PREFIX=mgmt_prefix)
        update_settings(TINC_PORT_DFLT=tinc_port)
        
        context = {
            'net_name': TINC_NET_NAME,
            'tinc_conf': ( "BindToAddress = 0.0.0.0\n"
                           "Port = %s\n"
                           "Name = server\n"
                           "StrictSubnets = True" % tinc_port ),
            'tinc_up': tinc_server.get_tinc_up(),
            'tinc_down': tinc_server.get_tinc_down(),
            'mgmt_prefix': mgmt_prefix.split('::')[0],
            'user': username }
        
        r = functools.partial(run, silent=False)
        if run("grep %(net_name)s /etc/tinc/nets.boot" % context).return_code == 1:
            e("echo %(net_name)s >> /etc/tinc/nets.boot" % context)
        r("mkdir -p /etc/tinc/%(net_name)s/hosts" % context)
        r("echo '%(tinc_conf)s' > /etc/tinc/%(net_name)s/tinc.conf" % context)
        # TODO get from tinc model!
        r('echo "Subnet = %(mgmt_prefix)s:0:0:0:0:2/128" > /etc/tinc/%(net_name)s/hosts/server' % context)
        r("echo '%(tinc_up)s' > /etc/tinc/%(net_name)s/tinc-up" % context)
        r("echo '%(tinc_down)s' > /etc/tinc/%(net_name)s/tinc-down" % context)
        r("chown %(user)s /etc/tinc/%(net_name)s/hosts" % context)
        r("chmod +x /etc/tinc/%(net_name)s/tinc-up" % context)
        r("chmod +x /etc/tinc/%(net_name)s/tinc-down" % context)
        
        if not protect:
            r('tincd -n %(net_name)s -K' % context)
            # Get created pubkey
            pubkey = ''
            for line in file('/etc/tinc/%s/hosts/server' % TINC_NET_NAME):
                pubkey += line
                if line == '-----BEGIN RSA PUBLIC KEY-----\n':
                    pubkey = line
                elif line == '-----END RSA PUBLIC KEY-----\n':
                    break
            tinc_server.pubkey = pubkey
            tinc_server.save()
        
        self.stdout.write('Tincd server successfully created and configured.')
        self.stdout.write(' * You may want to start it: /etc/init.d/tinc restart')

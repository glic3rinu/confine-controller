import getpass, pwd, re, os, functools
from optparse import make_option

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from M2Crypto import BIO, RSA

from controller.settings import MGMT_IPV6_PREFIX
from controller.utils import update_settings
from controller.utils.system import check_root, run, get_default_celeryd_username
from nodes.models import Server

from mgmtnetworks.tinc.settings import TINC_NET_NAME, TINC_PORT_DFLT, TINC_TINCD_ROOT


class Command(BaseCommand):
    """
    Creates the tincd config files and Server.tinc object.
    
    This method must be called by a superuser
    """
    
    def __init__(self, *args, **kwargs):
        # Options are defined in an __init__ method to support swapping out
        # custom user models in tests.
        super(Command, self).__init__(*args, **kwargs)
        default_username = get_default_celeryd_username()
        self.option_list = BaseCommand.option_list + (
            make_option('--username', dest='username', default=default_username,
                help='Specifies the login for the superuser.'),
            make_option('--mgmt_prefix', dest='mgmt_prefix', default=MGMT_IPV6_PREFIX,
                help='Mgmt prefix, the settings file will be updated.'),
            make_option('--tinc_port_dflt', dest='tinc_port_dflt', default=TINC_PORT_DFLT,
                help='Tinc port default, the settings file will be updated.'),
            make_option('--tinc_address', dest='tinc_address', default='0.0.0.0',
                help='Tinc BindToAddress'),
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
        from mgmtnetworks.tinc.models import TincServer, TincAddress
        interactive = options.get('interactive')
        username = options.get('username')
        
        if not interactive:
            # validate username
            if not username:
                raise CommandError("You must use --username with --noinput.")
            try:
                username = pwd.getpwnam(username).pw_name
            except KeyError:
                raise CommandError("Username doesn't exists.")
        else:
            # Prompt for username
            # Enclose this whole thing in a try/except to trap for a
            # keyboard interrupt and exit gracefully.
            prompt_username = None
            while prompt_username is None:
                if not prompt_username:
                    input_msg = "Celeryd username"
                    if username:
                        input_msg += " (leave blank to use '%s')" % username
                    raw_value = raw_input(input_msg + ': ')
                if username and raw_value == '':
                    raw_value = username
                # validate username
                try:
                    prompt_username = pwd.getpwnam(raw_value).pw_name
                except KeyError:
                    self.stderr.write("Error: %s" % '; '.join(e.messages))
                    prompt_username = None
                    continue
        
        server_ct = ContentType.objects.get_for_model(Server)
        tinc_server, created = TincServer.objects.get_or_create(object_id=1, content_type=server_ct)
        
        tinc_port = options.get('tinc_port_dflt')
        tinc_address = options.get('tinc_address')
        mgmt_prefix = options.get('mgmt_prefix')
        update_settings(MGMT_IPV6_PREFIX=mgmt_prefix)
        update_settings(TINC_PORT_DFLT=tinc_port)
        
        context = {
            'tincd_root': TINC_TINCD_ROOT,
            'net_name': TINC_NET_NAME,
            'net_root': os.path.join(TINC_TINCD_ROOT, TINC_NET_NAME),
            'tinc_conf': ( "BindToAddress = %s\n"
                           "Port = %s\n"
                           "Name = server\n"
                           "StrictSubnets = True" % (tinc_address, tinc_port)),
            'tinc_up': tinc_server.get_tinc_up(),
            'tinc_down': tinc_server.get_tinc_down(),
            'mgmt_prefix': mgmt_prefix.split('::')[0],
            'user': username }
        
        r = functools.partial(run, silent=False)
        if run("grep %(net_name)s %(tincd_root)s/nets.boot" % context, err_codes=[0,1]).return_code == 1:
            r("echo %(net_name)s >> %(tincd_root)s/nets.boot" % context)
        r("mkdir -p %(net_root)s/hosts" % context)
        r("echo '%(tinc_conf)s' > %(net_root)s/tinc.conf" % context)
        r('echo "Subnet = %(mgmt_prefix)s:0:0:0:0:2/128" > %(net_root)s/hosts/server' % context)
        r("echo '%(tinc_up)s' > %(net_root)s/tinc-up" % context)
        r("echo '%(tinc_down)s' > %(net_root)s/tinc-down" % context)
        r("chown %(user)s %(net_root)s/hosts" % context)
        r("chmod +x %(net_root)s/tinc-up" % context)
        r("chmod +x %(net_root)s/tinc-down" % context)
        
        if tinc_address != '0.0.0.0':
            TincAddress.objects.get_or_create(server=tinc_server, addr=tinc_address, port=tinc_port)
        
        priv_key = os.path.join(TINC_TINCD_ROOT, TINC_NET_NAME, 'rsa_key.priv')
        try:
            priv_key = RSA.load_key(priv_key)
        except:
            # generate a new key
            r('tincd -c %(net_root)s -K' % context)
            priv_key = RSA.load_key(priv_key)
        
        bio = BIO.MemoryBuffer()
        priv_key.save_pub_key_bio(bio)
        pub_key = bio.getvalue()
        
        tinc_server.pubkey = pub_key
        tinc_server.save()
        
        
        self.stdout.write('Tincd server successfully created and configured.')

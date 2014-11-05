import functools
import pwd
import os
from optparse import make_option

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.six.moves import input
from M2Crypto import BIO, RSA

from controller import settings
from controller.utils import update_settings
from controller.utils.system import check_root, run, get_default_celeryd_username
from nodes.models import Server

from tinc.settings import (TINC_NET_NAME, TINC_PORT_DFLT,
    TINC_TINCD_ROOT, TINC_TINCD_BIN, TINC_TINCD_SEND_HUP)


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
            make_option('--mgmt_prefix', dest='mgmt_prefix',
                default=settings.MGMT_IPV6_PREFIX,
                help='Mgmt prefix, the settings file will be updated.'),
            make_option('--default_port', dest='default_port',
                default=TINC_PORT_DFLT,
                help='Tinc port default, the settings file will be updated.'),
            make_option('--address', dest='address', default='0.0.0.0',
                help='Tinc BindToAddress'),
            make_option('--net_name', dest='net_name', default=TINC_NET_NAME,
                help='Tinc net name'),
            make_option('--nohup', dest='nohup', default=TINC_TINCD_SEND_HUP,
                help='Whether we want to send a HUP signal to tinc after an update'
                     ' or not. It requires sudo'),
            make_option('--noinput', action='store_false', dest='interactive',
                help='Tells Django to NOT prompt the user for input of any kind. '
                     'You must use --username with --noinput, and must contain the '
                     'cleeryd process owner, which is the user how will perform '
                     'tincd updates', default=True),
            )
    
    option_list = BaseCommand.option_list
    help = 'Creates the tincd config files and Server.tinc object'
    
    @transaction.atomic
    @check_root
    def handle(self, *args, **options):
        from tinc.models import TincHost, TincAddress
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
                    value = input(input_msg + ': ')
                if username and value == '':
                    value = username
                # validate username
                try:
                    prompt_username = pwd.getpwnam(value).pw_name
                except KeyError, e:
                    self.stderr.write("Error: %s" % e)
                    prompt_username = None
                    continue
        
        server = Server.objects.first()
        server_ct = ContentType.objects.get_for_model(Server)
        tinc_server, __ = TincHost.objects.get_or_create(object_id=server.pk,
            content_type=server_ct)
        
        tinc_port = options.get('default_port')
        tinc_address = options.get('address')
        tinc_net_name = options.get('net_name')
        mgmt_prefix = options.get('mgmt_prefix')
        
        if mgmt_prefix != settings.MGMT_IPV6_PREFIX:
            update_settings(MGMT_IPV6_PREFIX=mgmt_prefix,
                            monkey_patch='controller.settings')
        if tinc_port != TINC_PORT_DFLT:
            update_settings(TINC_PORT_DFLT=tinc_port)
        if tinc_net_name != TINC_NET_NAME:
            update_settings(TINC_NET_NAME=tinc_net_name)
        
        context = {
            'tincd_root': TINC_TINCD_ROOT,
            'tincd_bin': TINC_TINCD_BIN,
            'net_name': tinc_net_name,
            'net_root': os.path.join(TINC_TINCD_ROOT, tinc_net_name),
            'tinc_conf': (
                "BindToAddress = %s\n"
                "Port = %s\n"
                "Name = server\n"
                "StrictSubnets = yes" % (tinc_address, tinc_port)),
            'tinc_up': tinc_server.get_tinc_up(),
            'tinc_down': tinc_server.get_tinc_down(),
            'mgmt_prefix': mgmt_prefix.split('::')[0],
            'user': username }
        
        r = functools.partial(run, silent=False)
        boots = run("grep %(net_name)s %(tincd_root)s/nets.boot" % context, err_codes=[0,1])
        if boots.return_code == 1:
            r("echo %(net_name)s >> %(tincd_root)s/nets.boot" % context)
        r("mkdir -p %(net_root)s/hosts" % context)
        r("echo '%(tinc_conf)s' > %(net_root)s/tinc.conf" % context)
        r('echo "Subnet = %(mgmt_prefix)s:0:0:0:0:2/128" > %(net_root)s/hosts/server' % context)
        r("echo '%(tinc_up)s' > %(net_root)s/tinc-up" % context)
        r("echo '%(tinc_down)s' > %(net_root)s/tinc-down" % context)
        r("chown %(user)s %(net_root)s/hosts" % context)
        r("chmod +x %(net_root)s/tinc-up" % context)
        r("chmod +x %(net_root)s/tinc-down" % context)
        
        TincAddress.objects.get_or_create(host=tinc_server, addr=tinc_address,
                port=tinc_port)
        
        priv_key = os.path.join(TINC_TINCD_ROOT, tinc_net_name, 'rsa_key.priv')
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
        
        if options.get('nohup'):
            sudoers_hup = (
                "%(user)s\s\s*ALL=NOPASSWD:\s\s*%(tincd_bin)s\s\s*-kHUP\s\s*-n %(net_name)s"
            ) % context
            sudoers_exists = run('grep "%s" /etc/sudoers' % sudoers_hup, err_codes=[0,1,2])
            if sudoers_exists.return_code == 1:
                cmd = "%(user)s ALL=NOPASSWD: %(tincd_bin)s -kHUP -n %(net_name)s" % context
                r("echo '%s' >> /etc/sudoers" % cmd)
            elif sudoers_exists.return_code == 2:
                raise CommandError('Sudo is not installed on your system. \n'
                    'You may want to use --nohup option, so sudo will not be a requirement')
        else:
            update_settings(TINC_TINCD_SEND_HUP=False)
        self.stdout.write('Tincd server successfully created and configured.')
        self.stdout.write('NOTE: restarting the following services is required '
                          'to apply updated configuration:\n'
                          'tincd, uwsgi, celeryd.\n'
                          'Please run: "sudo python manage.py restartservices" or '
                          'restart them manually.')

import getpass
from subprocess import Popen, PIPE

from django.core.management.base import BaseCommand, CommandError

from nodes.models import Server
from nodes.settings import MGMT_IPV6_PREFIX


class Command(BaseCommand):
    """
    Creates the tincd config files and Server.tinc object.
    
    This method must be called by a superuser
    """
    
    help = 'Creates the tincd config files and Server.tinc object'
    
    def handle(self, *args, **options):
        if getpass.getuser() != 'root':
            raise CommandError('Sorry, create_tinc_server must be executed as a superuser (root)')
        
        from tinc.models import TincServer
        from tinc.settings import TINC_NET_NAME
        server = Server.objects.get_or_create(id=1)
        tinc_server = TincServer.objects.filter(object_id=1, content_type__model='server', 
                                                content_type__app_label='nodes') 
        if tinc_server.exists():
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
        cmd = "tinc/scripts/create_server.sh %s %s" % (TINC_NET_NAME, MGMT_IPV6_PREFIX.split('::')[0])
        cmd = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = cmd.communicate()
        if cmd.returncode > 0:
            raise CreateTincdError(stderr)
        
        pubkey = ''
        for line in file('/etc/tinc/%s/hosts/server' % TINC_NET_NAME):
            pubkey += line
            if line == '-----BEGIN RSA PUBLIC KEY-----\n':
                pubkey = line
            elif line == '-----END RSA PUBLIC KEY-----\n':
                break
        
        tinc_server.pubkey = pubkey
        tinc_server.save()
        
        # TODO get celery user
        cmd = """chown %(user)s /etc/tinc/%(net)s/hosts;
                 chmod o+x /etc/tinc/%(net)s/tinc-{up,down}""" % {'net': TINC_NET_NAME, 'user': 'confine'}
        cmd = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = cmd.communicate()
        if cmd.returncode > 0:
            raise self.CreateTincdError(stderr)
    
        self.stdout.write('Tincd server successfully created and configured.')
        self.stdout.write(' * You may want to start it: /etc/init.d/tinc start')
    
    class CreateTincdError(Exception): pass

import os
from optparse import make_option

from django.core.management.base import BaseCommand

from controller.utils.paths import get_site_root
from controller.utils.system import run, get_default_celeryd_username


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
                help='Specifies username crontab'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Creates the crontab for running the local monitoring script'
    
    def handle(self, *args, **options):
        context = {
                'username': options.get('username'),
                'manage_file': os.path.join(get_site_root(), 'manage.py'),
            }
        exists = "crontab -u %(username)s -l | grep ' monitorlocalsystem' &> /dev/null"
        exists = run(exists % context, display=False, err_codes=[0,1]).return_code
        if exists != 0:
            cmd = (
                '{ crontab -l -u %(username)s;'
                '  echo "*/5 * * * *   python %(manage_file)s monitorlocalsystem --email --quiet"; '
                '} | crontab -u %(username)s -') % context
            cmd = run(cmd)
            print cmd.return_code
        else:
            self.stdout.write('Done nothing, crontab was already installed')

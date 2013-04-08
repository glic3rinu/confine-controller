from optparse import make_option
from os import path

from django.conf import settings
from django.core.management.base import BaseCommand

from controller.utils.paths import get_site_root, get_controller_root
from controller.utils.system import run, check_root


#TODO rename -> setupcelery 

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--username', dest='username', default='confine',
                help='Specifies the system user that would generate the firmwares.'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '
                     'You must use --username with --noinput, and must contain the '
                     'cleleryd process owner, which is the user how will perform tincd updates'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Configure Celeryd to run with your controller instance.'
    
    @check_root
    def handle(self, *args, **options):
        context = {'site_root': get_site_root(),
                   'username': options.get('username'),
                   'bin_path': path.join(get_controller_root(), 'bin') }
        
        celery_config = (
            '# Name of nodes to start, here we have a single node\n'
            'CELERYD_NODES="w1 w2"\n'
            '\n'
            '# Where to chdir at start.\n'
            'CELERYD_CHDIR="%(site_root)s"\n'
            '\n'
            '# How to call "manage.py celeryd_multi"\n'
            'CELERYD_MULTI="$CELERYD_CHDIR/manage.py celeryd_multi"\n'
            '\n'
            '# Extra arguments to celeryd\n'
            'CELERYD_OPTS="-P:w1 processes -P:w2 gevent -c:w1 8 -c:w2 1000 \\\n'
            '              -Q:w1 celery -Q:w2 gevent --time-limit=400"\n'
            '\n'
            '# Name of the celery config module.\n'
            'CELERY_CONFIG_MODULE="celeryconfig"\n'
            '\n'
            '# %%n will be replaced with the nodename.\n'
            'CELERYD_LOG_FILE="/var/log/celery/%%n.log"\n'
            'CELERYD_PID_FILE="/var/run/celery/%%n.pid"\n'
            '\n'
            '# Full path to the celeryd logfile.\n'
            'CELERYEV_LOG_FILE="/var/log/celery/celeryev.log"\n'
            'CELERYEV_PID_FILE="/var/run/celery/celeryev.pid"\n'
            '\n'
            '# Workers should run as an unprivileged user.\n'
            'CELERYD_USER="%(username)s"\n'
            'CELERYD_GROUP="$CELERYD_USER"\n'
            '\n'
            'CELERYEV_USER="$CELERYD_USER"\n'
            'CELERYEV_GROUP="$CELERYD_USER"\n'
            '\n'
            '# Path to celeryd\n'
            'CELERYEV="$CELERYD_CHDIR/manage.py"\n'
            '\n'
            '# Extra arguments to manage.py\n'
            'CELERYEV_OPTS="celeryev"\n'
            '\n'
            '# Camera class to use (required)\n'
            'CELERYEV_CAM="djcelery.snapshot.Camera"\n'
            '\n'
            '# Celerybeat\n'
            'CELERYBEAT_CHDIR="$CELERYD_CHDIR"\n'
            'CELERYBEAT="${CELERYBEAT_CHDIR}/manage.py celerybeat"\n'
            'CELERYBEAT_OPTS="--schedule=/var/run/celerybeat-schedule"\n'
            '\n'
            '# Persistent revokes\n'
            'CELERYD_STATE_DB="$CELERYD_CHDIR/persistent_revokes"\n' % context)
        
        run("echo '%s' > /etc/default/celeryd" % celery_config)
        
        # https://raw.github.com/celery/celery/master/extra/generic-init.d/
        for script in ['celeryd', 'celeryevcam', 'celerybeat']:
            context['script'] = script
            run('cp %(bin_path)s/%(script)s /etc/init.d/%(script)s' % context)
            run('chmod +x /etc/init.d/%(script)s' % context)
            run('update-rc.d %(script)s defaults' % context)
        
        rotate = ('/var/log/celery/*.log {\n'
                  '    weekly\n'
                  '    missingok\n'
                  '    rotate 10\n'
                  '    compress\n'
                  '    delaycompress\n'
                  '    notifempty\n'
                  '    copytruncate\n'
                  '}')
        run("echo '%s' > /etc/logrotate.d/celeryd" % rotate)

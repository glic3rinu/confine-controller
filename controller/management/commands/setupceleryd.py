import warnings

from optparse import make_option
from os import path

from django.core.management.base import BaseCommand, CommandError

from controller.utils.paths import get_site_root, get_controller_root
from controller.utils.system import run, check_root


#TODO rename -> setupcelery 

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--username', dest='username', default='',
                help='Deprecated. Use --user instead.'),
            make_option('--user', dest='user', default='',
                help='Specifies the system user that would run celery tasks.'),
            make_option('--group', dest='group', default='',
                help='Specifies the system group that would run celery tasks.'),
            make_option('--processes', dest='processes', default=5,
                help='Number of celeryd processes.'),
            make_option('--greenlets', dest='greenlets', default=1000,
                help='Number of celeryd greenlets (gevent-based tasks).'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind.'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Configure Celeryd to run with your controller instance.'
    
    @check_root
    def handle(self, *args, **options):
        if options.get('username'):
            warnings.warn('"username" has been deprecated in favor of "user"', DeprecationWarning)
        if options.get('user') and options.get('username'):
            raise CommandError("Only one of this options should be provided: --user OR --username")
        
        user = options.get('user') or options.get('username') or 'confine'
        context = {'site_root': get_site_root(),
                   'user': user,
                   'group': options.get('group') or user,
                   'bin_path': path.join(get_controller_root(), 'bin'),
                   'processes': options.get('processes'),
                   'greenlets': options.get('greenlets') }
        
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
            'CELERYD_OPTS="-P:w1 processes -c:w1 %(processes)s -Q:w1 celery \\\n'
            '              -P:w2 gevent -c:w2 %(greenlets)s -Q:w2 gevent --time-limit=300"\n'
            '\n'
            '# Name of the celery config module.\n'
            'CELERY_CONFIG_MODULE="celeryconfig"\n'
            '\n'
            '# %%n will be replaced with the nodename.\n'
            'CELERYD_LOG_FILE="/var/log/celery/%%n.log"\n'
            'CELERYD_PID_FILE="/var/run/celery/%%n.pid"\n'
            'CELERY_CREATE_DIRS=1\n'
            '\n'
            '# Full path to the celeryd logfile.\n'
            'CELERYEV_LOG_FILE="/var/log/celery/celeryev.log"\n'
            'CELERYEV_PID_FILE="/var/run/celery/celeryev.pid"\n'
            '\n'
            '# Workers should run as an unprivileged user.\n'
            'CELERYD_USER="%(user)s"\n'
            'CELERYD_GROUP="%(group)s"\n'
            '\n'
            '# Persistent revokes\n'
            'CELERYD_STATE_DB="$CELERYD_CHDIR/persistent_revokes"\n'
            '\n'
            '# Celeryev\n'
            'CELERYEV="$CELERYD_CHDIR/manage.py"\n'
            'CELERYEV_CAM="djcelery.snapshot.Camera"\n'
            'CELERYEV_USER="$CELERYD_USER"\n'
            'CELERYEV_GROUP="$CELERYD_GROUP"\n'
            'CELERYEV_OPTS="celeryev"\n'
            '\n'
            '# Celerybeat\n'
            'CELERYBEAT="${CELERYD_CHDIR}/manage.py celerybeat"\n'
            'CELERYBEAT_USER="$CELERYD_USER"\n'
            'CELERYBEAT_GROUP="$CELERYD_GROUP"\n'
            'CELERYBEAT_CHDIR="$CELERYD_CHDIR"\n'
            'CELERYBEAT_OPTS="--schedule=/var/run/celerybeat-schedule"\n' % context)
        
        run("echo '%s' > /etc/default/celeryd" % celery_config)
        
        # https://raw.github.com/celery/celery/master/extra/generic-init.d/
        for script in ['celeryevcam', 'celeryd', 'celerybeat']:
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

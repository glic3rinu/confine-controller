import re
from optparse import make_option

from django.core.management.base import BaseCommand

from controller.utils import is_installed
from controller.utils.system import run, check_root


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--development', action='store_true', dest='development', default=False,
                help='Only install development requirements'),
            make_option('--local', action='store_true', dest='local', default=False,
                help='Only install local requirements'),
            make_option('--no-restart', action='store_false', dest='restart', default=True,
                help='Only install local requirements'),
            make_option('--specifics', action='store_true', dest='specifics_only',
                default=False, help='Only run version specific operations'),
            make_option('--no-upgrade-notes', action='store_false', default=True,
                dest='print_upgrade_notes', help='Do not print specific upgrade notes'),
            make_option('--from', dest='version', default=False,
                help="Controller's version from where you are upgrading, i.e 0.6.32"),
            )
    
    option_list = BaseCommand.option_list
    help = 'Upgrades confine-controller installation'
    # This command must be able to run in an environment with unsatisfied dependencies
    can_import_settings = False
    requires_model_validation = False
    
    @check_root
    def handle(self, *args, **options):
        version = options.get('version')
        upgrade_notes = []
        if version:
            version_re = re.compile(r'^\s*(\d+)\.(\d+)\.(\d+).*')
            minor_release = version_re.search(version)
            if minor_release is not None:
                major, major2, minor = version_re.search(version).groups()
            else:
                version_re = re.compile(r'^\s*(\d+)\.(\d+).*')
                major, major2 = version_re.search(version).groups()
                minor = 0
            # Represent version as two digits per number: 1.2.2 -> 10202
            version = int(str(major) + "%02d" % int(major2) + "%02d" % int(minor))
            
            # Pre version specific upgrade operations
            if version < 835:
                # prevent schema migrations from failing
                if is_installed('firmware'):
                    from firmware.models import Build
                    Build.objects.filter(base_image=None).update(base_image='')
            if version <= 902:
                if is_installed('maintenance'):
                    # Apply losed migrations
                    from south.models import MigrationHistory
                    migrated = MigrationHistory.objects.filter(app_name='maintenance').exists()
                    if not migrated:
                        run('python manage.py migrate maintenance 0001 --fake')
        
        if not options.get('specifics_only'):
            # Common stuff
            development = options.get('development')
            local = options.get('local')
            if local:
                run("controller-admin.sh install_requirements --local")
            else:
                extra = '--development' if development else ''
                run("controller-admin.sh install_requirements " + extra)
                run("python manage.py collectstatic --noinput")
            
            run("python manage.py syncdb")
            run("python manage.py migrate")
            if is_installed('firmware'):
                run("python manage.py syncfirmwareplugins")
            if is_installed('notifications'):
                run("python manage.py syncnotifications")
            if options.get('restart'):
                run("python manage.py restartservices")
        
        if not version:
            self.stderr.write('\nNext time you migth want to provide a --from argument '
                              'in order to run version specific upgrade operations\n')
            return
        
        # Post version specific operations
        if version <= 629:
            # Clean existing sessions because of change on auth backend
            run('echo "delete from django_session;" | python manage.py dbshell')
        if version < 801:
            # Deprecate ping.state
            from djcelery.models import PeriodicTask
            PeriodicTask.objects.filter(name='state.ping').delete()
            run('rabbitmqctl stop_app')
            run('rabbitmqctl reset')
            run('rabbitmqctl start_app')
            run('service celeryd restart')
        if version < 809:
            # Add PKI directories
            from pki import ca
            from controller.utils.paths import get_site_root
            from os import path
            site_root = get_site_root()
            username = run("stat -c %%U %s" % site_root)
            get_dir = lambda f: path.dirname(getattr(ca, f+'_path'))
            for d in set( get_dir(f) for f in ['priv_key', 'pub_key', 'cert'] ):
                run('mkdir -p %s' % d)
                run('chown %s %s' % (username, d))
            upgrade_notes.append('HTTPS certificate support for the management '
                'network has been introduced in version 0.8.9.\n'
                'In order to use it you sould run:\n'
                '  > python manage.py setuppki\n'
                '  > sudo python manage.py setupapache\n')
        if version < 838:
            # Purge communitynetworks.periodic_cache_node_db
            from djcelery.models import PeriodicTask
            PeriodicTask.objects.filter(name='communitynetworks.periodic_cache_node_db').delete()
            run('rabbitmqctl stop_app')
            run('rabbitmqctl reset')
            run('rabbitmqctl start_app')
            run('service celeryd restart')
            upgrade_notes.append('New Celeryd init.d configuration has been '
                'introduced in 0.8.38.\nIt is strongly recommended to upgrade by\n'
                '  > sudo python manage.py setupceleryd\n')
            # Deprecate x86 and amd64 architectures
            from nodes.models import Node
            Node.objects.filter(arch='x86').update(arch='i686')
            Node.objects.filter(arch='amd64').update(arch='x86_64')
            upgrade_notes.append('In order to support Base authentication while downloading '
                'firmwares you should add "WSGIPassAuthorization On" on your apache config.\n'
                'Alternatively you can perform this operation with the following command\n'
                '  > sudo python manage.py setupapache\n'
                '  > /etc/init.d/apache2 reload\n')
        if version < 900:
            upgrade_notes.append('Apache configuration is now placed under '
                '/etc/apache2/conf.d/<project_name>.conf. It is convenient for you '
                'to migrate your current configuration located on /etc/apache2/httpd.conf '
                'to this new location.\n')
            upgrade_notes.append('Celery workers configuration has been updated. '
                'Please update it by running:\n'
                '  > sudo python manage.py setupceleryd\n')
        if upgrade_notes and options.get('print_upgrade_notes'):
            self.stdout.write('\n\033[1m\n'
                '    ===================\n'
                '    ** UPGRADE NOTES **\n'
                '    ===================\n\n' +
                '\n'.join(upgrade_notes) + '\033[m\n')


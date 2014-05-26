import re
import os
from optparse import make_option

from django.core.management.base import BaseCommand

from controller.utils.apps import is_installed
from controller.utils.system import run, check_root


def deprecate_periodic_tasks(names):
    from djcelery.models import PeriodicTask
    for name in names:
        PeriodicTask.objects.filter(name=name).delete()
    run('rabbitmqctl stop_app')
    run('rabbitmqctl reset')
    run('rabbitmqctl start_app')
    run('service celeryd restart')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--development', action='store_true', dest='development', default=False,
                help='Only install development requirements'),
            make_option('--no-restart', action='store_false', dest='restart', default=True,
                help='Do not restart services'),
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
    leave_locale_alone = True
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
            
            # Pre-upgrade operations (version specific)
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
            if version < 1002:
                # Update monitor settings (fix typo and add DiskFreeMonitor)
                context = {
                    'settings': run("find . -type f -name 'settings.py'|grep -v 'vct/'")
                }
                # Try automaticate update (making a backup)
                if context['settings']:
                    run("cp %(settings)s %(settings)s.upgrade.bak" % context)
                    # fix NumProcessesMonitor typo
                    run("sed -i 's/NumPocessesMonitor/NumProcessesMonitor/g' "
                        "%(settings)s" % context)
                    # append disk monitor (if needed)
                    # this is a rude check (but runned in a conservative way)
                    if 'DiskFreeMonitor' not in open(context['settings']).read():
                        run("sed -i '/MONITOR_MONITORS = ($/ a\ "
                            "   (\"monitor.monitors.DiskFreeMonitor\",),' "
                            "%(settings)s" % context)
                # warn the user about settings changes
                autoupdate_status = 'OK' if context['settings'] else 'FAIL'
                upgrade_notes.append('The monitor application has changed and .'
                    'some settings updates are required:\n'
                    ' - Fix typo on NumProcessesMonitor (missing "r")\n'
                    ' - Enable disk monitor\n'
                    ' Please read the monitor app doc (MONITOR_MONITORS setting)\n'
                    'AUTOUPDATE: %s' % autoupdate_status)
        
        if not options.get('specifics_only'):
            # Common stuff
            development = options.get('development')
            controller_admin = os.path.join(os.path.dirname(__file__), '../../bin/')
            controller_admin = os.path.join(controller_admin, 'controller-admin.sh')
            run('chmod +x %s' % controller_admin)
            
            extra = '--development' if development else ''
            run("%s install_requirements " % controller_admin + extra)
            run("python manage.py collectstatic --noinput")
            
            run("python manage.py syncdb --noinput")
            run("python manage.py migrate --noinput")
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
        
        # Post-upgrade operations (version specific)
        if version <= 629:
            # Clean existing sessions because of change on auth backend
            run('echo "delete from django_session;" | python manage.py dbshell')
        if version < 801:
            deprecate_periodic_tasks(('state.ping',))
        if version < 809:
            # Add PKI directories
            from pki import ca
            from controller.utils.paths import get_site_root
            site_root = get_site_root()
            username = run("stat -c %%U %s" % site_root)
            get_dir = lambda f: os.path.dirname(getattr(ca, f+'_path'))
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
        if version < 905:
            # TODO find the root cause of this
            # maybe is shit imported on settings that import settings like add_app
            # Prevent crazy import erros to appear :S
            from django.utils import translation
            translation.activate('en-us')
            # Change template types for more generic ones
            from slices.models import Template
            from slices.settings import SLICES_TEMPLATE_TYPES
            template_types = [ t[0] for t in SLICES_TEMPLATE_TYPES ]
            if 'debian' in template_types:
                Template.objects.filter(type='debian6').update(type='debian')
            if 'openwrt' in template_types:
                Template.objects.filter(type='openwrt-backfire').update(type='openwrt')
        if version < 906:
            deprecate_periodic_tasks(('state.nodestate', 'state.sliverstate'))
        if version <= 907:
            # Generate sha256
            from slices.models import Template
            for template in Template.objects.all():
                template.save()
            upgrade_notes.append("It is extremly recommended to update your database "
                "settings to enable atomic request behaviour:\n"
                "  https://docs.djangoproject.com/en/dev/topics/db/transactions/#tying-transactions-to-http-requests\n"
                "Just add:\n"
                "   'ATOMIC_REQUESTS': True,\n"
                "into DATABASES setting within <project_name>/<project_name>/settings.py")
        if version <= 1003:
            # Update firmware configuration after Island refactor (#264)
            from firmware.models import ConfigFile
            try:
                cfg_file = ConfigFile.objects.get(path__contains="node.tinc.connect_to")
            except (ConfigFile.DoesNotExist, ConfigFile.MultipleObjectsReturned):
                # Warn the user that needs to perform manual update
                msg = "Firmware configuration update has failed. "
            else:
                cfg_file.content = cfg_file.content.replace("node.tinc.island", "node.island")
                msg = "Firmware configuration updated successfully. Updated ConfigFile ID: %i." % cfg_file.pk
            upgrade_notes.append("%s\nPlease check version 0.10.4 release notes:\n"
                "https://wiki.confine-project.eu/soft:server-release-notes#section0104" % msg)
        
        if upgrade_notes and options.get('print_upgrade_notes'):
            self.stdout.write('\n\033[1m\n'
                '    ===================\n'
                '    ** UPGRADE NOTES **\n'
                '    ===================\n\n' +
                '\n'.join(upgrade_notes) + '\033[m\n')

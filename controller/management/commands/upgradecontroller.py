import functools
import os
import random
import string
from optparse import make_option

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from controller import get_version
from controller.utils import decode_version
from controller.utils import get_existing_pip_installation
from controller.utils.system import run, check_root


r = functools.partial(run, silent=False)


def validate_controller_version(version):
    if not version or version == 'dev':
        return
    try:
        decode_version(version)
    except ValueError as e:
        raise CommandError(e)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--pip_only', action='store_true', dest='pip_only', default=False,
                help='Only run "pip install confine-controller --upgrade"'),
            make_option('--controller_version', dest='version', default=False,
                help='Specifies what version of the controller you want to install'),
            make_option('--proxy', dest='proxy',
                help='Specify a proxy in the form [user:passwd@]proxy.server:port.'),
            )
    
    option_list = BaseCommand.option_list
    help = "Upgrading controller's installation"
    can_import_settings = False
    leave_locale_alone = True
    
    @check_root
    def handle(self, *args, **options):
        current_version = get_version()
        current_path = get_existing_pip_installation()
        proxy = '--proxy %s' % options.get('proxy') if options.get('proxy') else ''
        
#        # Getting version that will be installed, yeah pip doesn't support it :)
#        pypi_url = 'https://pypi.python.org/pypi/confine-controller'
#        grep = 'href="/pypi?:action=doap&amp;name=confine-controller&amp;version='
#        extract = '| head -n1 | cut -d"=" -f5 | cut -d\'"\' -f1'
#        pypi_version = "wget -q '%s' -O - | grep '%s' %s" % (pypi_url, grep, extract)
#        pypi_version = run(pypi_version).stdout
#        
#        if current_version == pypi_version:
#            msg = "Not upgrading, you already have version %s installed"
#            raise CommandError(msg % current_version)
        
        if current_path is not None:
            desired_version = options.get('version')
            validate_controller_version(desired_version)
            if current_version == desired_version:
                msg = "Not upgrading, you already have version %s installed"
                raise CommandError(msg % desired_version)
            # Create a backup of current installation
            base_path = os.path.abspath(os.path.join(current_path, '..'))
            char_set = string.ascii_uppercase + string.digits
            rand_name = ''.join(random.sample(char_set, 6))
            backup = os.path.join(base_path, 'controller.' + rand_name)
            run("mv %s %s" % (current_path, backup))
            
            # collect existing eggs previous to the installation
            eggs_regex = os.path.join(base_path, 'confine_controller-*.egg-info')
            eggs = run('ls -d %s' % eggs_regex)
            eggs = eggs.stdout.splitlines()
            try:
                if desired_version:
                    # if desired_version == 'dev':
                    #     r('pip install -e git+http://git.confine-project.eu/confine/controller.git@master#egg=confine-controller')
                    # else:
                        r('pip %s install confine-controller==%s' % (proxy, desired_version))
                else:
                    # Did I mentioned how I hate PIP?
                    if run('pip --version|cut -d" " -f2').stdout == '1.0':
                        r('pip %s install confine-controller --upgrade' % proxy)
                    else:
                        # (Fucking pip)^2, it returns exit code 0 even when fails
                        # because requirement already up-to-date
                        r('pip %s install confine-controller --upgrade --force' % proxy)
            except CommandError:
                # Restore backup
                run('rm -rf %s' % current_path)
                run('mv %s %s' % (backup, current_path))
                raise CommandError("Problem runing pip upgrade, aborting...")
            else:
                # Some old versions of pip do not performe this cleaning ...
                # Remove all backups
                run('rm -fr %s' % os.path.join(base_path, 'controller\.*'))
                # Clean old egg files, yeah, cleaning PIP shit :P
                c_version = 'from controller import get_version; print get_version()'
                version = run('python -c "%s;"' % c_version).stdout
                for egg in eggs:
                    # Do not remove the actual egg file when upgrading twice the same version
                    if egg.split('/')[-1] != "confine_controller-%s.egg-info" % version:
                        run('rm -fr %s' % egg)
        else:
            raise CommandError("You don't seem to have any previous PIP installation")
        
        # version specific upgrade operations
        if not options.get('pip_only'):
            call_command("postupgradecontroller", version=current_version,
                proxy=options.get('proxy'))

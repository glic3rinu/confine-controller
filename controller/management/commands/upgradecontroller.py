import os, random, string
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from controller import get_version
from controller.utils import get_existing_pip_installation
from controller.utils.system import run, check_root


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--pip', action='store_true', dest='pip_only', default=False,
                help='Only run "pip install confine-controller --upgrade"'),
            )
    
    option_list = BaseCommand.option_list
    help = "Upgrading controller's installation"
    
    @check_root
    def handle(self, *args, **options):
        current_version = get_version()
        current_path = get_existing_pip_installation()
        
        if current_path is not None:
            # Create a backup of current installation
            base_path = os.path.abspath(os.path.join(current_path, '..'))
            char_set = string.ascii_uppercase + string.digits
            rand_name = ''.join(random.sample(char_set, 6))
            backup = os.path.join(base_path, 'controller.' + rand_name)
            run("mv %s %s" % (current_path, backup))
            
            # collect existing eggs previous to the installation
            eggs = run('ls -d %s' % os.path.join(base_path, 'confine_controller-*.egg-info'))
            eggs = eggs.stdout.splitlines()
            
            try:
                run('pip install confine-controller --upgrade', silent=False)
            except CommandError:
                # Restore backup
                run('rm -rf %s' % current_path)
                run('mv %s %s' % (backup, current_path))
                raise CommandError("Problem runing pip upgrade, aborting...")
            else:
                # Remove the backup
                run('rm -fr %s' % backup)
                for egg in eggs:
                    run('rm -r %s' % egg)
        else:
            raise CommandError("You don't seems to have any previous PIP installation")
        
        # version specific upgrade operations
        if not options.get('pip_only'):
            run("python manage.py upgrade --from %s" % current_version)

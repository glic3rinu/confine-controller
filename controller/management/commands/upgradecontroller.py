import os, random, string

from django.core.management.base import BaseCommand, CommandError

from controller.utils import get_existing_pip_installation
from controller.utils.system import run, check_root


class Command(BaseCommand):
    help = 'Just performs a pip install confine-controller --upgrade, but deleting previos installations'
    
    @check_root
    def handle(self, *args, **options):
        current_path = get_existing_pip_installation()
        if current_path is not None:
            # Create a backup of current installation
            base_path = os.path.abspath(os.path.join(current_path, '..'))
            char_set = string.ascii_uppercase + string.digits
            rand_name = ''.join(random.sample(char_set,6))
            backup = os.path.join(base_path, 'controller.' + rand_name)
            run("mv %s %s" % (current_path, backup))
            
            try:
                self.stderr.write("\nThe next command can take a while to report feedback, be patient ...")
                run('pip install confine-controller --upgrade', silent=False)
            except CommandError:
                # Restore backup
                run('rm -rf %s' % current_path)
                run('mv %s %s' % (backup, current_path))
                raise CommandError("Problem runing pip upgrade, aborting...")
            else:
                # Remove the backup
                run('rm -fr %s' % backup)
            
        else:
            raise CommandError("You don't seems to have any previous PIP installation")

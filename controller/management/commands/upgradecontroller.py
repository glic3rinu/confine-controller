import os, random, string, sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from controller.utils import get_existing_pip_installation
from controller.utils.system import run, check_root


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--pip_only', action='store_false', dest='full_upgrade', default=True,
                help='Just perform pip install confine-controller --upgrade'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Upgrades confine controller installation'
    
    @check_root
    def handle(self, *args, **options):
        current_path = get_existing_pip_installation()
        full_upgrade = options.get('full_upgrade')
        if current_path is not None:
            # Create a backup of current installation
            base_path = os.path.abspath(os.path.join(current_path, '..'))
            char_set = string.ascii_uppercase + string.digits
            rand_name = ''.join(random.sample(char_set,6))
            backup = os.path.join(base_path, 'controller.' + rand_name)
            run("mv %s %s" % (current_path, backup))
            
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
            
            if full_upgrade:
                sys.stderr.write("\nThe next command can take a while to run, be patient ....")
                run("controller-admin.sh install_requirements")
                run("python manage.py collectstatic --noinput")
        else:
            if full_upgrade:
                sys.stderr.write("\nYou don't currently seems to have any pip made installation "
                             "of confine-controller.\nAssuming development installation...")
                sys.stderr.write("\nThe next command can take a while to run, be patient ....")
                run("controller-admin.sh install_requirements --minimal")
            else:
                raise CommandError("You don't seems to have any previous installation")
        
        if full_upgrade:
            run("python manage.py syncdb")
            run("python manage.py migrate")
            run("python manage.py restartservices")

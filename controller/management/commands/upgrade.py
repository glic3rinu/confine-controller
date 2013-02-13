from optparse import make_option

from django.core.management.base import BaseCommand

from controller.utils.system import run, check_root


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--minimal', action='store_true', dest='minimal', default=false,
                help='Only install minimal requirements'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Upgrades confine controller installation'
    
    @check_root
    def handle(self, *args, **options):
        minimal = options.get('minimal')
        self.stderr.write("\nThe next command can take a while to report feedback, be patient ...")
        if minimal:
            run("controller-admin.sh install_requirements --minimal")
        else:
            run("controller-admin.sh install_requirements")
            run("python manage.py collectstatic --noinput")
        run("python manage.py syncdb")
        run("python manage.py migrate")
        run("python manage.py restartservices")

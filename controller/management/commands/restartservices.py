from optparse import make_option

from django.core.management.base import BaseCommand

from controller.utils.system import run, check_root


# TODO refactor this to a BaseServiceCommand or something

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--no-apache', action='store_false', dest='apache', default=True,
                help='No apache.'),
            make_option('--no-tinc', action='store_false', dest='tinc', default=True,
                help='No tinc.'),
            make_option('--no-celeryd', action='store_false', dest='celeryd', default=True,
                help='No celeryd.'),
            make_option('--no-celeryevcam', action='store_false', dest='celeryevcam', default=True,
                help='No celeryevcam.'),
            make_option('--no-postgresql', action='store_false', dest='postgresql', default=True,
                help='No postgresql.'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Restars all related services. Usefull for reload configuration and files.'
    
    @check_root
    def handle(self, *args, **options):
        if options.get('tinc'):
            run('service tinc restart')
        if options.get('apache'):
            run('service apache2 restart')
        if options.get('celeryd'):
            run('service celeryd restart')
        if options.get('celerybeat'):
            run('service celerybeat restart')
        if options.get('celeryevcam'):
            run('service celeryevcam restart')
        if options.get('postgresql'):
            run('service postgresql restart')

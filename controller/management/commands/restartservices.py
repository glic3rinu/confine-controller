from django.core.management.base import BaseCommand

from controller.utils.system import run, check_root


class Command(BaseCommand):
    help = 'Restars all related services. Usefull for reload configuration and files.'
    
    @check_root
    def handle(self, *args, **options):
        run('service tinc restart')
        run('service apache2 restart')
        run('service celeryd restart')
        run('service celeryevcam restart')

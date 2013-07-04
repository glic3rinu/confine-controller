from django.core.management.base import BaseCommand

from controller.management.commands.startservices import ManageServiceCommand


class Command(ManageServiceCommand):
    services = ['celeryd', 'celerybeat', 'apache2']
    action = 'restart'
    option_list = BaseCommand.option_list
    help = 'Restart all related services. Usefull for reload configuration and files.'

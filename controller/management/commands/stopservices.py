from django.core.management.base import BaseCommand

from controller.management.commands.startservices import ManageServiceCommand


class Command(ManageServiceCommand):
    services = ['apache2', 'celerybeat', 'celeryd', 'celeryevcam', 'tinc', 'postgresql']
    action = 'stop'
    option_list = BaseCommand.option_list
    help = 'Stop all related services. Usefull for reload configuration and files.'

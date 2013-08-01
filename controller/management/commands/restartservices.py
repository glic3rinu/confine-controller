from django.core.management.base import BaseCommand

from controller.management.commands.startservices import ManageServiceCommand
from controller.settings import RESTART_SERVICES


class Command(ManageServiceCommand):
    services = RESTART_SERVICES
    action = 'restart'
    option_list = BaseCommand.option_list
    help = 'Restart all related services. Usefull for reload configuration and files.'

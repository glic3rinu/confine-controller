from django.core.management.base import BaseCommand

from controller.management.commands.startservices import ManageServiceCommand
from controller.settings import STOP_SERVICES


class Command(ManageServiceCommand):
    services = STOP_SERVICES
    action = 'stop'
    option_list = BaseCommand.option_list
    help = 'Stop all related services. Usefull for reload configuration and files.'

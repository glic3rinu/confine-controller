from optparse import make_option

from django.core.management.base import BaseCommand

from controller.utils.system import run, check_root


class ManageServiceCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(ManageServiceCommand, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + tuple(
            make_option('--no-%s' % service, action='store_false', dest=service, default=True,
                 help='Do not %s %s' % (self.action, service)) for service in self.services
            )
    
    @check_root
    def handle(self, *args, **options):
        for service in self.services:
            if options.get(service):
                run('service %s %s' % (service, self.action))


class Command(ManageServiceCommand):
    services = ['postgresql', 'tinc', 'celeryevcam', 'celeryd', 'celerybeat', 'apache2']
    action = 'start'
    option_list = BaseCommand.option_list
    help = 'Start all related services. Usefull for reload configuration and files.'

from django.core.management.base import NoArgsCommand

from controller import get_version


class Command(NoArgsCommand):
    help = 'Shows confine-controller version'

    def handle_noargs(self, **options):
        self.stdout.write(get_version())

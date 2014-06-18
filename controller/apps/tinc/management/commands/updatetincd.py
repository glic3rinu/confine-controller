from django.core.management.base import BaseCommand

from tinc.tasks import update_tincd


class Command(BaseCommand):
    help = 'Updates tincd hosts files according to information stored on the database.'
    
    def handle(self, *args, **options):
        update_tincd()

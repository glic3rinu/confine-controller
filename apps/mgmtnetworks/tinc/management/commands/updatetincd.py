from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Updates tincd hosts files according to information stored on the database.'
    
    def handle(self, *args, **options):
        from mgmtnetworks.tinc.tasks import update_tincd
        update_tincd()

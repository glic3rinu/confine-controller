from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from firmware.models import Config, ConfigPlugin
from firmware.plugins import FirmwarePlugin


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list
    
    option_list = BaseCommand.option_list
    help = 'Sync existing plugins with the database'
    
    def handle(self, *args, **options):
        config = Config.objects.get()
        existing_pks = []
        for plugin in FirmwarePlugin.plugins:
            label = plugin.__name__
            obj, __ = ConfigPlugin.objects.get_or_create(config=config, label=label,
                description=plugin.description)
            existing_pks.append(obj.pk)
        # Delete unused plugins
        ConfigPlugin.objects.exclude(pk__in=existing_pks).delete()

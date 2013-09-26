from django.core.management.base import BaseCommand

from firmware.models import Config, ConfigPlugin
from firmware.plugins import FirmwarePlugin


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list
    
    option_list = BaseCommand.option_list
    help = 'Sync existing plugins with the database'
    
    def handle(self, *args, **options):
        config, __ = Config.objects.get_or_create(pk=1)
        existing_pks = []
        for plugin in FirmwarePlugin.plugins:
            label = plugin.__name__
            module = plugin.__module__
            obj, __ = ConfigPlugin.objects.get_or_create(config=config, label=label,
                module=module)
            existing_pks.append(obj.pk)
            self.stdout.write('Found %s (%s)' % (label, module))
        # Delete unused plugins
        ConfigPlugin.objects.exclude(pk__in=existing_pks).delete()

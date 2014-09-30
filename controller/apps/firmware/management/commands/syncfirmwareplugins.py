from django.core.management.base import BaseCommand

from firmware.models import Config, ConfigPlugin
from firmware.plugins import FirmwarePlugin


class Command(BaseCommand):
    help = 'Synchronize existing firmware plugins with the database.'
    
    def handle(self, *args, **options):
        config, __ = Config.objects.get_or_create(pk=1)
        existing_pks = []
        for plugin in FirmwarePlugin.plugins:
            label = plugin.__name__
            module = plugin.__module__
            is_active = plugin.enabled_by_default
            obj, __ = ConfigPlugin.objects.get_or_create(config=config,
                label=label, module=module, defaults={'is_active': is_active})
            existing_pks.append(obj.pk)
            self.stdout.write('Found %s (%s)' % (label, module))
        # Delete unused plugins
        ConfigPlugin.objects.exclude(pk__in=existing_pks).delete()

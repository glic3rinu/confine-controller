from django.apps import AppConfig

from controller.utils import autodiscover


class SlicesConfig(AppConfig):
    name = 'controller.apps.slices'
    
    def ready(self):
        autodiscover('ifaces')

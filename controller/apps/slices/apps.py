from django.apps import AppConfig

from controller.utils import autodiscover


class SlicesConfig(AppConfig):
    name = 'slices'
    
    def ready(self):
        autodiscover('ifaces')

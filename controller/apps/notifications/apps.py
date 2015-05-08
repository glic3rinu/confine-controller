from django.apps import AppConfig

from controller.utils import autodiscover


class NotificationsConfig(AppConfig):
    name = 'controller.apps.notifications'
    
    def ready(self):
        autodiscover('notifications')

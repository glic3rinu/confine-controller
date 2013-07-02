from controller.utils import autodiscover

from .options import Notification


# Autodiscover notifications.py
# Making sure models are loaded first in order to avoid circular imports !
#autodiscover('models')
autodiscover('notifications')

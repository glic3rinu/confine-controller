from controller.utils import autodiscover

from .options import *

# Autodiscover permissions.py
# Making sure models are loaded first in order to avoid circular imports !
autodiscover('models')
autodiscover('permissions')

REQUIRED_APPS = ['django.contrib.admin']

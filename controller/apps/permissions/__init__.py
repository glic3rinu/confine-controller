from controller.utils import autodiscover

from .permissions import *

# Autodiscover permissions.py
# Making sure models are loaded first in order to avoid circular imports !
autodiscover('models')
autodiscover('permissions')

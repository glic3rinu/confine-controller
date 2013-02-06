from controller.utils import autodiscover

from .permissions import Permission, ReadOnlyPermission, AllowAllPermission


# Autodiscover permissions.py
autodiscover('permissions')

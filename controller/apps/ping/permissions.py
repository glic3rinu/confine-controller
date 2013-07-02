from __future__ import absolute_import

from permissions import ReadOnlyPermission

from .models import Ping


Ping.has_permission = ReadOnlyPermission()

from __future__ import absolute_import

from permissions import ReadOnlyPermission

from .models import Ping


class PingPermission(ReadOnlyPermission):
    def change(self, cls, obj, user):
        if obj:
            return obj.content_object.has_permission.change(user)
        return False

Ping.has_permission = PingPermission()

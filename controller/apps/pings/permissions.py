from __future__ import absolute_import

from permissions import ReadOnlyPermission

from .models import Ping


class PingPermission(ReadOnlyPermission):
    """ Allow delete because this is a related object """
    def delete(self, obj, cls, user):
        if obj is None:
            return True
        return obj.content_object.has_permission.delete(user)


Ping.has_permission = PingPermission()

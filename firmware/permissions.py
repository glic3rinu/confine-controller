from __future__ import absolute_import
import inspect

from nodes.models import Node
from permissions import Permission


class FirmwarePermission(Permission):
    def getfirmware(self, caller, user):
        if not inspect.isclass(caller):
            if caller.group.has_roles(user, roles=['admin', 'technician']):
                return True
        return False


Node.has_permission._aggregate(FirmwarePermission())

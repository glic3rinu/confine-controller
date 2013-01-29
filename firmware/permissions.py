from __future__ import absolute_import

from nodes.models import Node
from permissions import Permission


class FirmwarePermission(Permission):
    def getfirmware(self, caller, user):
        if not self.is_class(caller):
            if caller.group.has_roles(user, roles=['admin', 'technician']):
                return True
        return False


Node.has_permission._aggregate(FirmwarePermission())

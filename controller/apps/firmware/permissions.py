from __future__ import absolute_import

from nodes.models import Node
from permissions import Permission

from .models import Build


class FirmwarePermission(Permission):
    def getfirmware(self, obj, cls, user):
        if obj is not None:
            return obj.group.has_roles(user, roles=['admin', 'technician'])
        return False


class BuildPermission(Permission):
    """ Allow delete nodes """
    def delete(self, obj, cls, user):
        if obj is not None:
            # TODO This will never be executed on admin because admin.delete checks
            # permissions like a bitch, without passing the object:
            # if not user.has_perm(p): perms_needed.add(opts.verbose_name)
            # Maybe we can open a ticket and fix this shit
            # https://github.com/django/django/blob/master/django/contrib/admin/util.py
            return obj.node.group.has_roles(user, roles=['admin', 'technician'])
        return True


Node.has_permission._aggregate(FirmwarePermission())
Build.has_permission = BuildPermission()

from __future__ import absolute_import

from permissions import ReadOnlyPermission

from .models import Report, State


class StatePermission(ReadOnlyPermission):
    """ Allow delete because this is a node related object """
    def delete(self, obj, cls, user):
        if obj is None:
            return user.has_roles(('admin', 'technician'))
        return obj.node.group.has_roles(user, roles=['admin', 'technician'])

class ReportPermission(ReadOnlyPermission):
    pass

Report.has_permission = ReportPermission()
State.has_permission = StatePermission()


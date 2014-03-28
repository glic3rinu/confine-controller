from __future__ import absolute_import

from permissions import ReadOnlyPermission

from .models import State, StateHistory


class StatePermission(ReadOnlyPermission):
    """ Allow delete because this is a node related object """
    def delete(self, obj, cls, user):
        if obj is None:
            return user.has_roles(('group_admin', 'node_admin'))
        return obj.node.group.has_roles(user, roles=['group_admin', 'node_admin'])


State.has_permission = StatePermission()
StateHistory.has_permission = StatePermission()

from __future__ import absolute_import

from permissions import ReadOnlyPermission

from .models import NodeState, SliverState


class NodeStatePermission(ReadOnlyPermission):
    def delete(self, caller, user):
        if self._is_class(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.node.group.has_roles(user, roles=['admin', 'technician'])


class SliverStatePermission(ReadOnlyPermission):
    def delete(self, caller, user):
        if self._is_class(caller):
            return user.has_role('admin')
        return caller.sliver.group.has_roles(user, roles=['admin'])


NodeState.has_permission = NodeStatePermission()
SliverState.has_permission = SliverStatePermission()

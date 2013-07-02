from __future__ import absolute_import

from permissions import ReadOnlyPermission

from .models import NodeState, SliverState


class NodeStatePermission(ReadOnlyPermission):
    def change(self, obj, cls, user):
        if obj is None:
            return user.has_roles(('admin', 'technician'))
        return obj.node.group.has_roles(user, roles=['admin', 'technician'])


class SliverStatePermission(ReadOnlyPermission):
    def change(self, obj, cls, user):
        if obj is None:
            return user.has_roles(('admin', 'researcher'))
        return obj.sliver.group.has_roles(user, roles=['admin', 'researcher'])


NodeState.has_permission = NodeStatePermission()
SliverState.has_permission = SliverStatePermission()

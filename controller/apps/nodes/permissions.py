from __future__ import absolute_import

from permissions import Permission, ReadOnlyPermission, RelatedPermission

from .models import DirectIface, Island, Node, NodeProp, Server


class NodePermission(Permission):
    admins = ('group_admin', 'node_admin')

    def view(self, obj, cls, user):
        return True
    
    def add(self, obj, cls, user):
        """ group and node admins can add """
        if obj is None:
            allow_nodes = user.groups.filter(allow_nodes=True).exists()
            return user.has_roles(self.admins) and allow_nodes
        if obj.group.allow_nodes:
            return obj.group.has_roles(user, roles=self.admins)
    
    def change(self, obj, cls, user):
        """ group and node admins can change """
        if obj is None:
            return user.has_roles(self.admins)
        allow_nodes = user.groups.filter(allow_nodes=True).exists()
        return obj.group.has_roles(user, roles=self.admins) and allow_nodes
    
    def delete(self, obj, cls, user):
        """ group and node admins can delete """
        if obj is None:
            return user.has_roles(self.admins)
        return obj.group.has_roles(user, roles=self.admins)


Node.has_permission = NodePermission()
NodeProp.has_permission = RelatedPermission('node')
DirectIface.has_permission = RelatedPermission('node')
Server.has_permission = ReadOnlyPermission()
Island.has_permission = ReadOnlyPermission()

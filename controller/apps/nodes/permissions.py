from __future__ import absolute_import

from permissions import Permission, ReadOnlyPermission, RelatedPermission

from .models import Node, NodeProp, DirectIface, Server


class NodePermission(Permission):
    def view(self, obj, cls, user):
        return True
    
    def add(self, obj, cls, user):
        """ Admins and techs can add """
        if obj is None:
            allow_nodes = user.groups.filter(allow_nodes=True).exists()
            return user.has_roles(('admin', 'technician')) and allow_nodes
        if obj.group.allow_nodes:
            return obj.group.has_roles(user, roles=['admin', 'technician'])
    
    def change(self, obj, cls, user):
        """ group admins and techs can change """
        if obj is None:
            return user.has_roles(('admin', 'technician'))
        allow_nodes = user.groups.filter(allow_nodes=True).exists()
        return obj.group.has_roles(user, roles=['admin', 'technician']) and allow_nodes
    
    def delete(self, obj, cls, user):
        """ group admins and techs can delete """
        if obj is None:
            return user.has_roles(('admin', 'technician'))
        return obj.group.has_roles(user, roles=['admin', 'technician'])


Node.has_permission = NodePermission()
NodeProp.has_permission = RelatedPermission('node')
DirectIface.has_permission = RelatedPermission('node')
Server.has_permission = ReadOnlyPermission()

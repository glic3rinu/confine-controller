from __future__ import absolute_import

from permissions import Permission, ReadOnlyPermission, RelatedPermission

from .models import Node, NodeProp, DirectIface, Server


class NodePermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if self._is_class(caller):
            allow_nodes = user.groups.filter(allow_nodes=True).exists()
            return user.has_roles(('admin', 'technician')) and allow_nodes
        if caller.group.allow_nodes:
            return caller.group.has_roles(user, roles=['admin', 'technician'])
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if self._is_class(caller):
            return user.has_roles(('admin', 'technician'))
        allow_nodes = user.groups.filter(allow_nodes=True).exists()
        return caller.group.has_roles(user, roles=['admin', 'technician']) and allow_nodes
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        if self._is_class(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.group.has_roles(user, roles=['admin', 'technician'])


Node.has_permission = NodePermission()
NodeProp.has_permission = RelatedPermission('node')
DirectIface.has_permission = RelatedPermission('node')
Server.has_permission = ReadOnlyPermission()

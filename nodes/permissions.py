from __future__ import absolute_import

from permissions import Permission, ReadOnlyPermission

from .models import Node, NodeProp, DirectIface, Server


class NodePermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if self.is_class(caller):
            return user.has_roles(('admin', 'technician'))
        if caller.group.allow_nodes:
            return caller.group.has_roles(user, roles=['admin', 'technician'])
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if self.is_class(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.group.has_roles(user, roles=['admin', 'technician'])
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        if self.is_class(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.group.has_roles(user, roles=['admin', 'technician'])


class NodePropPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if self.is_class(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.node.group.has_roles(user, roles=['admin', 'technician'])
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if self.is_class(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.node.group.has_role(user, roles=['admin', 'technician'])
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        if self.is_class(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.node.group.has_roles(user, roles=['admin', 'technician'])


class DirectIfacePermission(NodePropPermission):
    pass


Node.has_permission = NodePermission()
NodeProp.has_permission = NodePropPermission()
DirectIface.has_permission = DirectIfacePermission()
Server.has_permission = ReadOnlyPermission()

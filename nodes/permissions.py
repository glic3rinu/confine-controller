from __future__ import absolute_import
import inspect

from permissions import Permission, ReadOnlyPermission

from .models import Node, NodeProp, DirectIface, Server


class NodePermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        if caller.group.allow_nodes:
            if caller.group.has_roles(user, roles=['admin', 'technician']):
                return True
        return False
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.group.has_roles(user, roles=['admin', 'technician'])
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.group.has_roles(user, roles=['admin', 'technician'])


class NodePropPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        elif caller.node.group.has_roles(user, roles=['admin', 'technician']):
            return True
        return False
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.node.group.has_role(user, roles=['admin', 'technician'])
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.node.group.has_roles(user, roles=['admin', 'technician'])


class DirectIfacePermission(NodePropPermission):
    pass


Node.has_permission = NodePermission()
NodeProp.has_permission = NodePropPermission()
DirectIface.has_permission = DirectIfacePermission()
Server.has_permission = ReadOnlyPermission()

from __future__ import absolute_import

from permissions import Permission, ReadOnlyPermission

from .models import Node, NodeProp, DirectIface, Server


class NodePermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if self.is_class(caller):
            allow_nodes = user.groups.filter(allow_nodes=True).exists()
            return user.has_roles(('admin', 'technician')) and allow_nodes
        if caller.group.allow_nodes:
            return caller.group.has_roles(user, roles=['admin', 'technician'])
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if self.is_class(caller):
            return user.has_roles(('admin', 'technician'))
        allow_nodes = user.groups.filter(allow_nodes=True).exists()
        return caller.group.has_roles(user, roles=['admin', 'technician']) and allow_nodes
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        if self.is_class(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.group.has_roles(user, roles=['admin', 'technician'])


class NodeRelatedPermission(NodePermission):
    def add(self, caller, user):
        """ Admins and techs can add """
        parent = caller if self.is_class(caller) else caller.node
        return super(NodeRelatedPermission, self).add(parent, user)
    
    def change(self, caller, user):
        """ group admins and techs can change """
        parent = caller if self.is_class(caller) else caller.node
        return super(NodeRelatedPermission, self).change(parent, user)
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        parent = caller if self.is_class(caller) else caller.node
        return super(NodeRelatedPermission, self).delete(parent, user)


Node.has_permission = NodePermission()
NodeProp.has_permission = NodeRelatedPermission()
DirectIface.has_permission = NodeRelatedPermission()
Server.has_permission = NodeRelatedPermission()

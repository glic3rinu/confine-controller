import inspect

from users.permissions import Permission

from .models import Node, NodeProp, DirectIface


class NodePermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if inspect.isclass(caller):
            if user.roles.intersection(('admin', 'tech')): 
                return True
            return False
        elif caller.group.has_roles(user, roles=['admin', 'tech']):
                return True
        return False
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if inspect.isclass(caller):
            if user.roles.intersection(('admin', 'tech')): 
                return True
            return False
        return caller.group.has_roles(user, roles=['admin', 'tech'])
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        return caller.group.has_roles(user, roles=['admin', 'tech'])


class NodePropPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if inspect.isclass(caller):
            if user.roles.intersection(('admin', 'tech')): 
                return True
            return False
        elif caller.node.group.has_roles(user, roles=['admin', 'tech']):
                return True
        return False
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if inspect.isclass(caller):
            if user.roles.intersection(('admin', 'tech')): 
                return True
            return False
        return caller.node.group.has_role(user, roles=['admin', 'tech'])
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        return caller.node.group.has_roles(user, roles=['admin', 'tech'])


class DirectIfacePermission(NodePropPermission):
    pass


Node.has_permission = NodePermission()
NodeProp.has_permission = NodePropPermission()
DirectIface.has_permission = DirectIfacePermission()

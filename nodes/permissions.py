import inspect

from users.permissions import Permission

from .models import Node, NodeProp, DirectIface


class NodePermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        elif caller.group.has_roles(user, roles=['admin', 'technician']):
            return True
        return False
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.group.has_roles(user, roles=['admin', 'technician'])
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        return caller.group.has_roles(user, roles=['admin', 'technician'])


class NodePropPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'tech'))
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
        return caller.node.group.has_roles(user, roles=['admin', 'technician'])


class DirectIfacePermission(NodePropPermission):
    pass


Node.has_permission = NodePermission()
NodeProp.has_permission = NodePropPermission()
DirectIface.has_permission = DirectIfacePermission()

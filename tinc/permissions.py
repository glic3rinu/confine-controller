import inspect

from users.permissions import Permission

from .models import TincClient, Host


class TincClientPermission(Permission):
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
        return caller.node.group.has_roles(user, roles=['admin', 'technician'])
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        return caller.node.group.has_roles(user, roles=['admin', 'technician'])


class HostPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        return True
    
    def change(self, caller, user):
        if inspect.isclass(caller):
            return True
        return caller.admin == user
    
    def delete(self, caller, user):
        return self.change(caller, user)


TincClient.has_permission = TincClientPermission()
Host.has_permission = HostPermission()

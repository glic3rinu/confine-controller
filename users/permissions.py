from __future__ import absolute_import
import inspect, functools

from permissions import Permission

from .models import User, AuthToken, Group, Roles


class UserPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        if inspect.isclass(caller):
            return True
        return caller == user
    
    def change(self, caller, user):
        return self.add(caller, user)
    
    def delete(self, caller, user):
        return self.add(caller, user)


class RolesPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.group.has_role(user, 'admin')
    
    def change(self, caller, user):
        return self.add(caller, user)
    
    def delete(self, caller, user):
        return self.add(caller, user)


class GroupPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        return True
    
    def change(self, caller, user):
        if inspect.isclass(caller):
            return False
        return caller.has_role(user, 'admin')
    
    def delete(self, caller, user):
        if inspect.isclass(caller):
            return True
        return caller.has_role(user, 'admin')


User.has_permission = UserPermission()
Roles.has_permission = RolesPermission()
Group.has_permission = GroupPermission()

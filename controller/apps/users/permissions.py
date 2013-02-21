from __future__ import absolute_import

from permissions import Permission, RelatedPermission

from .models import User, AuthToken, Group, Roles, JoinRequest


class UserPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        return False
    
    def change(self, caller, user):
        if self._is_class(caller):
            return True
        return caller == user
    
    def delete(self, caller, user):
        return self.change(caller, user)


class RolesPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        if self._is_class(caller):
            return user.has_role('admin')
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
        if self._is_class(caller):
            return True
        return caller.has_role(user, 'admin')
    
    def delete(self, caller, user):
        if self._is_class(caller):
            return True
        return caller.has_role(user, 'admin')


User.has_permission = UserPermission()
Roles.has_permission = RolesPermission()
Group.has_permission = GroupPermission()
AuthToken.has_permission = RelatedPermission('user')
JoinRequest.has_permission = RelatedPermission('group')

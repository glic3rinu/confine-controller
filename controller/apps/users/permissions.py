from __future__ import absolute_import

from permissions import Permission

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


class JoinRequestPermission(Permission):
    def view(self, caller, user):
        if self._is_class(caller):
            return True
        return caller.has_role(user, 'admin')
    
    def add(self, caller, user):
        return False
    
    def change(self, caller, user):
        if self._is_class(caller):
            return True
        return caller.group.has_role(user, 'admin')
    
    def delete(self, caller, user):
        return False


class AuthTokenPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        if self._is_class(caller):
            return True
        return caller.user == user
    
    def change(self, caller, user):
        if self._is_class(caller):
            return True
        return caller.user == user
    
    def delete(self, caller, user):
        if self._is_class(caller):
            return True
        return caller.user == user


User.has_permission = UserPermission()
Roles.has_permission = RolesPermission()
Group.has_permission = GroupPermission()
# RelatedPermission('user') can not be used because of userPerm.add == False
# TODO maybe relatedPermission can be rethought in a way that match this case?
AuthToken.has_permission = AuthTokenPermission()
JoinRequest.has_permission = JoinRequestPermission()

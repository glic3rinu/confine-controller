from __future__ import absolute_import

from permissions import Permission

from .models import User, AuthToken, Group, Roles, JoinRequest


class UserPermission(Permission):
    def view(self, obj, cls, user):
        return True
    
    def add(self, obj, cls, user):
        return False
    
    def change(self, obj, cls, user):
        if obj is None:
            return True
        return obj == user
    
    def delete(self, obj, cls, user):
        return self.change(obj, cls, user)


class RolesPermission(Permission):
    def view(self, obj, cls, user):
        return True
    
    def add(self, obj, cls, user):
        if obj is None:
            return True
        return obj.group.has_role(user, 'group_admin')
    
    def change(self, obj, cls, user):
        return self.add(obj, cls, user)
    
    def delete(self, obj, cls, user):
        return self.add(obj, cls, user)


class GroupPermission(Permission):
    def view(self, obj, cls, user):
        return True
    
    def add(self, obj, cls, user):
        return True
    
    def change(self, obj, cls, user):
        if obj is None:
            return True
        return obj.has_role(user, 'group_admin')
    
    def delete(self, obj, cls, user):
        if obj is None:
            return True
        return obj.has_role(user, 'group_admin')


class JoinRequestPermission(Permission):
    def view(self, obj, cls, user):
        if obj is None:
            return user.has_role('group_admin')
        return obj.group.has_role(user, 'group_admin')
    
    def add(self, obj, cls, user):
        return False
    
    def change(self, obj, cls, user):
        if obj is None:
            return True
        return obj.group.has_role(user, 'group_admin')
    
    def delete(self, obj, cls, user):
        return False


class AuthTokenPermission(Permission):
    def view(self, obj, cls, user):
        return True
    
    def add(self, obj, cls, user):
        if obj is None:
            return True
        return obj.user == user
    
    def change(self, obj, cls, user):
        if obj is None:
            return True
        return obj.user == user
    
    def delete(self, obj, cls, user):
        if obj is None:
            return True
        return obj.user == user


User.has_permission = UserPermission()
Roles.has_permission = RolesPermission()
Group.has_permission = GroupPermission()
# RelatedPermission('user') can not be used because of userPerm.add == False
# TODO maybe relatedPermission can be rethought in a way that match this case?
AuthToken.has_permission = AuthTokenPermission()
JoinRequest.has_permission = JoinRequestPermission()

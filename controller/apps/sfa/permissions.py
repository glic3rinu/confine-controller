from __future__ import absolute_import

from permissions import Permission
from users.models import Group

from .models import SfaObject

class SfaObjectPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins can add """
        if self._is_class(caller):
            return user.has_roles(('admin',))
        elif type(caller.content_object) is Group:
            return caller.content_object.has_role(user, 'admin')
        return caller.content_object.group.has_role(user, 'admin')
    
    def change(self, caller, user):
        """ Group admins can change """
        if self._is_class(caller):
            return user.has_roles(('admin',))
        elif type(caller.content_object) is Group:
            return caller.content_object.has_role(user, 'admin')
        return caller.content_object.group.has_role(user, 'admin')
    
    def delete(self, caller, user):
        """ Group admins can delete """
        if self._is_class(caller):
            return user.has_roles(('admin',))
        elif type(caller.content_object) is Group:
            return caller.content_object.has_role(user, 'admin')
        return caller.content_object.group.has_role(user, 'admin')


SfaObject.has_permission = SfaObjectPermission()

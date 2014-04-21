from __future__ import absolute_import

from permissions import Permission
from users.models import Group

from .models import SfaObject


class SfaObjectPermission(Permission):
    def view(self, obj, cls, user):
        return True
    
    def add(self, obj, cls, user):
        """ Admins can add """
        if obj is None:
            return user.has_roles(('group_admin',))
        elif isinstance(obj.content_object, Group):
            return obj.content_object.has_role(user, 'group_admin')
        return obj.content_object.group.has_role(user, 'group_admin')
    
    def change(self, obj, cls, user):
        """ Group admins can change """
        if obj is None:
            return user.has_roles(('group_admin',))
        elif isinstance(obj.content_object, Group):
            return obj.content_object.has_role(user, 'group_admin')
        return obj.content_object.group.has_role(user, 'group_admin')
    
    def delete(self, obj, cls, user):
        """ Group adminsobjcan delete """
        if obj is None:
            return user.has_roles(('group_admin',))
        elif isinstance(obj.content_object, Group):
            return obj.content_object.has_role(user, 'group_admin')
        return obj.content_object.group.has_role(user, 'group_admin')


SfaObject.has_permission = SfaObjectPermission()

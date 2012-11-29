from __future__ import absolute_import
import inspect

from permissions import Permission

from .models import CnHost

class CnHostPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        elif caller.content_object.group.has_roles(user, roles=['admin', 'technician']):
            return True
        return False
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.content_object.group.has_roles(user, roles=['admin', 'technician'])
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        return caller.content_object.group.has_roles(user, roles=['admin', 'technician'])


CnHost.has_permission = CnHostPermission()

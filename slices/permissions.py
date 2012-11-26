import inspect

from users.permissions import Permission

from .models import Slice, Sliver, SliceProp, SliverProp, Template

class SlicePermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        elif caller.group.has_role(user, 'admin'):
            return True
        return False
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.group.has_role(user, 'admin')
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        return caller.group.has_role(user, 'admin')


class SliverPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        elif caller.slice.group.has_role(user, 'admin'):
            return True
        return False
    
    def change(self, caller, user):
        """ Group admins can change """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.slice.group.has_role(user, 'admin')
    
    def delete(self, caller, user):
        """ Group admins can delete """
        return caller.slice.group.has_role(user, 'admin')


class SlicePropPermission(SliverPermission):
    pass


class SliverPropPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        elif caller.sliver.slice.group.has_role(user, 'admin'):
            return True
        return False
    
    def change(self, caller, user):
        """ Group admins can change """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.sliver.slice.group.has_role(user, 'admin')
    
    def delete(self, caller, user):
        """ Group admins can delete """
        return caller.sliver.slice.group.has_role(user, 'admin')


class TemplatePermission(Permission):
    def view(self, caller, user):
        return True


Slice.has_permission = SlicePermission()
Sliver.has_permission = SliverPermission()
SliceProp.has_permission = SlicePropPermission()
SliverProp.has_permission = SliverPropPermission()
Template.has_permission = TemplatePermission()

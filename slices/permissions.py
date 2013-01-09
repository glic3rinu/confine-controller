from __future__ import absolute_import
import inspect

from permissions import Permission, ReadOnlyPermission

from .models import Slice, Sliver, SliceProp, SliverProp, Template, SliverIface


class SlicePermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.group.allow_slices and caller.group.has_role(user, 'admin')
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.group.has_role(user, 'admin')
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.group.has_role(user, 'admin')


class SliverPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.slice.group.has_role(user, 'admin')
    
    def change(self, caller, user):
        """ Group admins can change """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.slice.group.has_role(user, 'admin')
    
    def delete(self, caller, user):
        """ Group admins can delete """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.slice.group.has_role(user, 'admin')


class SliverPropPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.sliver.slice.group.has_role(user, 'admin')
    
    def change(self, caller, user):
        """ Group admins can change """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.sliver.slice.group.has_role(user, 'admin')
    
    def delete(self, caller, user):
        """ Group admins can delete """
        if inspect.isclass(caller):
            return user.has_roles(('admin',))
        return caller.sliver.slice.group.has_role(user, 'admin')


Slice.has_permission = SlicePermission()
Sliver.has_permission = SliverPermission()
SliceProp.has_permission = SliverPermission()
SliverProp.has_permission = SliverPropPermission()
SliverIface.has_permission = SliverPropPermission()
Template.has_permission = ReadOnlyPermission()

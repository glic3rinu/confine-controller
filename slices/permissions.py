from __future__ import absolute_import

from permissions import Permission, ReadOnlyPermission

from .models import Slice, Sliver, SliceProp, SliverProp, Template, SliverIface


class SlicePermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins can add """
        if self.is_class(caller):
            allow_slices = user.groups.filter(allow_slices=True).exists()
            return user.has_roles(('admin',)) and allow_slices
        return caller.group.allow_slices and caller.group.has_role(user, 'admin')
    
    def change(self, caller, user):
        """ group admins can change """
        if self.is_class(caller):
            return user.has_roles(('admin',))
        allow_slices = user.groups.filter(allow_slices=True).exists()
        return caller.group.has_role(user, 'admin') and allow_slices
    
    def delete(self, caller, user):
        """ group admins can delete """
        if self.is_class(caller):
            return user.has_roles(('admin',))
        return caller.group.has_role(user, 'admin')


class SliceRelatedPermission(SlicePermission):
    def add(self, caller, user):
        """ Admins can add """
        parent = caller if self.is_class(caller) else caller.slice
        return super(SliceRelatedPermission, self).add(parent, user)
    
    def change(self, caller, user):
        """ Group admins can change """
        parent = caller if self.is_class(caller) else caller.slice
        return super(SliceRelatedPermission, self).change(parent, user)
    
    def delete(self, caller, user):
        """ Group admins can delete """
        parent = caller if self.is_class(caller) else caller.slice
        return super(SliceRelatedPermission, self).delete(parent, user)


class SliverRelatedPermission(SlicePermission):
    def add(self, caller, user):
        """ Admins can add """
        parent = caller if self.is_class(caller) else caller.sliver.slice
        return super(SliverRelatedPermission, self).add(parent, user)
    
    def change(self, caller, user):
        """ Group admins can change """
        parent = caller if self.is_class(caller) else caller.sliver.slice
        return super(SliverRelatedPermission, self).change(parent, user)
    
    def delete(self, caller, user):
        """ Group admins can delete """
        parent = caller if self.is_class(caller) else caller.sliver.slice
        return super(SliverRelatedPermission, self).delete(parent, user)


Slice.has_permission = SlicePermission()
Sliver.has_permission = SliceRelatedPermission()
SliceProp.has_permission = SliceRelatedPermission()
SliverProp.has_permission = SliverRelatedPermission()
SliverIface.has_permission = SliverRelatedPermission()
Template.has_permission = ReadOnlyPermission()

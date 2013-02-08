from __future__ import absolute_import

from permissions import Permission, ReadOnlyPermission, RelatedPermission

from .models import Slice, Sliver, SliceProp, SliverProp, Template, SliverIface


class SlicePermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins can add """
        if self._is_class(caller):
            allow_slices = user.groups.filter(allow_slices=True).exists()
            return user.has_roles(('admin',)) and allow_slices
        return caller.group.allow_slices and caller.group.has_role(user, 'admin')
    
    def change(self, caller, user):
        """ group admins can change """
        if self._is_class(caller):
            return user.has_roles(('admin',))
        allow_slices = user.groups.filter(allow_slices=True).exists()
        return caller.group.has_role(user, 'admin') and allow_slices
    
    def delete(self, caller, user):
        """ group admins can delete """
        if self._is_class(caller):
            return user.has_roles(('admin',))
        return caller.group.has_role(user, 'admin')


Slice.has_permission = SlicePermission()
Sliver.has_permission = RelatedPermission('slice')
SliceProp.has_permission = RelatedPermission('slice')
SliverProp.has_permission = RelatedPermission('sliver.slice')
SliverIface.has_permission = RelatedPermission('sliver.slice')
Template.has_permission = ReadOnlyPermission()

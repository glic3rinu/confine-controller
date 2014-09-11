from __future__ import absolute_import

from permissions import Permission, ReadOnlyPermission, RelatedPermission

from .models import (Slice, Sliver, SliverDefaults, Template, SliceProp,
    SliverProp, SliverIface)


class SlicePermission(Permission):
    admins = ('group_admin', 'slice_admin')
    
    def view(self, obj, cls, user):
        return True
    
    def add(self, obj, cls, user):
        if obj is None:
            allow_slices = user.groups.filter(allow_slices=True).exists()
            return user.has_roles(self.admins) and allow_slices
        return obj.group.allow_slices and obj.group.has_roles(user, self.admins)
    
    def change(self, obj, cls, user):
        if obj is None:
            return user.has_roles(self.admins)
        allow_slices = user.groups.filter(allow_slices=True).exists()
        return obj.group.has_roles(user, self.admins) and allow_slices
    
    def delete(self, obj, cls, user):
        if obj is None:
            return user.has_roles(self.admins)
        return obj.group.has_roles(user, self.admins)


Slice.has_permission = SlicePermission()
Sliver.has_permission = RelatedPermission('slice')
SliverDefaults.has_permission = RelatedPermission('slice')
SliceProp.has_permission = RelatedPermission('slice')
SliverProp.has_permission = RelatedPermission('sliver.slice')
SliverIface.has_permission = RelatedPermission('sliver.slice')
Template.has_permission = ReadOnlyPermission()

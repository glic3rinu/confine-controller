from __future__ import absolute_import

from permissions import Permission

from .models import Instance


class InstancePermission(Permission):
    admins = ('group_admin', 'node_admin')
    
    def delete(self, obj, cls, user):
        """ group and node admins can delete (#432) """
        if obj is None:
            return user.has_roles(self.admins)
        return obj.group.has_roles(user, roles=self.admins)


Instance.has_permission = InstancePermission()

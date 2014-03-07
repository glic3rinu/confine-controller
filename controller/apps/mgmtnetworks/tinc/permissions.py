from __future__ import absolute_import

from permissions import Permission, ReadOnlyPermission, AllowAllPermission

from .models import TincClient, TincServer, Host, Gateway, TincAddress


class HostPermission(Permission):
    def view(self, obj, cls, user):
        if obj is None:
            return True
        return obj.owner == user
    
    def add(self, obj, cls, user):
        return True
    
    def change(self, obj, cls, user):
        if obj is None:
            return True
        return obj.owner == user
    
    def delete(self, obj, cls, user):
        if obj is None:
            return True
        return self.change(obj, cls, user)


# Since it uses generic relations we must relay that permissions will be 
# handled by the parent object
TincClient.has_permission = AllowAllPermission()
TincServer.has_permission = ReadOnlyPermission()
Host.has_permission = HostPermission()
Gateway.has_permission = ReadOnlyPermission()
TincAddress.has_permission = ReadOnlyPermission()

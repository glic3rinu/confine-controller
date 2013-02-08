from __future__ import absolute_import

from permissions import Permission, ReadOnlyPermission, AllowAllPermission

from .models import TincClient, TincServer, Host, Gateway, Island, TincAddress


class HostPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        return True
    
    def change(self, caller, user):
        if self._is_class(caller):
            return True
        return caller.owner == user
    
    def delete(self, caller, user):
        if self._is_class(caller):
            return True
        return self.change(caller, user)

# Since it uses generic relations we must relay that permissions will be 
# handled by the parent object
TincClient.has_permission = AllowAllPermission()
TincServer.has_permission = ReadOnlyPermission()
Host.has_permission = HostPermission()
Gateway.has_permission = ReadOnlyPermission()
Island.has_permission = ReadOnlyPermission()
TincAddress.has_permission = ReadOnlyPermission()

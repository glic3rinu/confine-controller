from __future__ import absolute_import
import inspect

from permissions import Permission, ReadOnlyPermission

from .models import TincClient, TincServer, Host, Gateway, Island, TincAddress


class TincClientPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        """ Admins and techs can add """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.node.group.has_roles(user, roles=['admin', 'technician'])
    
    def change(self, caller, user):
        """ group admins and techs can change """
        if inspect.isclass(caller):
            return user.has_roles(('admin', 'technician'))
        return caller.node.group.has_roles(user, roles=['admin', 'technician'])
    
    def delete(self, caller, user):
        """ group admins and techs can delete """
        if inspect.isclass(caller):
            return True
        return caller.node.group.has_roles(user, roles=['admin', 'technician'])


class HostPermission(Permission):
    def view(self, caller, user):
        return True
    
    def add(self, caller, user):
        return True
    
    def change(self, caller, user):
        if inspect.isclass(caller):
            return True
        return caller.admin == user
    
    def delete(self, caller, user):
        if inspect.isclass(caller):
            return True
        return self.change(caller, user)


TincClient.has_permission = TincClientPermission()
TincServer.has_permission = ReadOnlyPermission()
Host.has_permission = HostPermission()
Gateway.has_permission = ReadOnlyPermission()
Island.has_permission = ReadOnlyPermission()
TincAddress.has_permission = ReadOnlyPermission()

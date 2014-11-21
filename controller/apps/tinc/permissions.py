from __future__ import absolute_import

from permissions import Permission, AllowAllPermission

from .models import TincHost, Host, TincAddress


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


class TincAddressPermission(Permission):
    def view(self, obj, cls, user):
        if obj is None:
            return True
        return True
    
    def add(self, obj, cls, user):
        return True
    
    def change(self, obj, cls, user):
        if obj is None:
            return True
        
        model = obj.host.content_type.model
        parent = obj.host.content_object
        if model == 'server':
            return False
        elif model == 'host':
            return parent.owner == user
        elif model == 'node':
            return parent.has_permission(user, 'change')
        
        raise RuntimeError('Unexpected content type "%(value)s" for TincHost '
                           '%(pk)s.' % {'value': model, 'pk': obj.host.pk})
    
    def delete(self, obj, cls, user):
        return self.change(obj, cls, user)


# Since it uses generic relations we must relay that permissions will be 
# handled by the parent object
TincHost.has_permission = AllowAllPermission()
Host.has_permission = HostPermission()
TincAddress.has_permission = TincAddressPermission()

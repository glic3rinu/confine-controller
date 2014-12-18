from rest_framework import exceptions
from rest_framework.permissions import DjangoObjectPermissions


class TestbedPermissionBackend(DjangoObjectPermissions):
    """
    Read only permissions for unauthenticated users,
    Write permissions according to each user.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'OPTIONS', 'HEAD']:
            # Read only permissions
            return True
        
        model_cls = getattr(view, 'model', None)
        if not model_cls:
            return True
        
        perms = self.get_required_permissions(request.method, model_cls)
        if (request.user and
            request.user.is_authenticated() and
            request.user.has_perms(perms, model_cls)):
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.method in ['GET', 'OPTIONS', 'HEAD']:
            # Read only permissions
            return True
        
        perms = self.get_required_permissions(request.method, type(obj))
        if (request.user and
            request.user.is_authenticated() and
            request.user.has_perms(perms, obj)):
            return True
        return False


class ApiPermissionsMixin(object):
    """ Hack for object-level ADD permission checking """
    def pre_save(self, obj):
        request = self.request
        if request.method == 'POST':
            model_cls = type(obj)
            context = {
                'app_label': model_cls._meta.app_label,
                'model_name': model_cls._meta.model_name, }
            perm = '%(app_label)s.add_%(model_name)s' % context
            if not request.user.has_perm(perm, obj):
                raise exceptions.PermissionDenied()

from rest_framework import exceptions
from rest_framework.permissions import DjangoModelPermissions


class TestbedPermissionBackend(DjangoModelPermissions):
    def has_permission(self, request, view, obj=None):
        if request.method in ['GET', 'OPTIONS', 'HEAD']:
            # Ronly Permissions
            return True
        
        model_cls = getattr(view, 'model', None)
        if not model_cls:
            return True
        perms = self.get_required_permissions(request.method, model_cls)
        if (request.user and
            request.user.is_authenticated() and
            request.user.has_perms(perms, obj)):
            return True
        return False


class ApiPermissionsMixin(object):
    """ Hack for ADD permissions checking """
    def pre_save(self, obj):
        request = self.request
        if request.method == 'POST':
            if not self.has_permission(request, obj):
                raise exceptions.PermissionDenied()

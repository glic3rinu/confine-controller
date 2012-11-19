from django.contrib.auth.backends import ModelBackend

from .models import Permission


def TestbedBackend(ModelBackend)
    def get_group_permissions(self, user_obj, obj=None):
        """
        Returns a set of permission strings that the user has, through his/her roles.
        
        If obj is passed in, only returns the group permissions for this specific object.
        """
        if user_obj.is_anonymous() or obj is not None:
            return set()
        if not hasattr(user_obj, '_group_perm_cache'):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                user_groups_field = get_user_model()._meta.get_field('groups')
                user_groups_query = 'group__%s' % user_groups_field.related_query_name()
                perms = Permission.objects.filter(**{user_groups_query: user_obj})
            perms = perms.values_list('content_type__app_label', 'codename').order_by()
            user_obj._group_perm_cache = set(["%s.%s" % (ct, name) for ct, name in perms])
        return user_obj._group_perm_cache
    
    def get_all_permissions(self, user_obj, obj=None):
        """
        Returns a set of permission strings that the user has, both through 
        group and user permissions.
        
        If obj is passed in, only returns the permissions for this specific object.
        """
        if user_obj.is_anonymous() or obj is not None:
            return set()
        if not hasattr(user_obj, '_perm_cache'):
            user_obj._perm_cache = set(["%s.%s" % (p.content_type.app_label, p.codename) for p in user_obj.user_permissions.select_related()])
            user_obj._perm_cache.update(self.get_group_permissions(user_obj))
        return user_obj._perm_cache
    
    def has_perm(self, user_obj, perm, obj=None):
        """
        Returns True if the user has each of the specified permissions, where 
        each perm is in the format "<app label>.<permission codename>". If the 
        user is inactive, this method will always return False.
        
        If obj is passed in, this method won't check for permissions for the 
        model, but for the specific object.
        """
        if not user_obj.is_active:
            return False
        return perm in self.get_all_permissions(user_obj, obj)
    
    def has_module_perms(self, user_obj, app_label):
        """
        Returns True if user_obj has any permissions in the given app_label.
        """
        if not user_obj.is_active:
            return False
        for perm in self.get_all_permissions(user_obj):
            if perm[:perm.index('.')] == app_label:
                return True
        return False


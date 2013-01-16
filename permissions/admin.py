from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib.contenttypes import generic
from django.core.exceptions import PermissionDenied
from django.forms.models import fields_for_model


class PermExtensionMixin(object):
    change_form_template = 'admin/permissions_change_form.html'
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make all fields read only if user doesn't have change permissions.
        """
        if not self.has_change_permission(request, obj=obj, view=False):
            if self.has_view_permission(request, obj=obj):
                excluded_fields = ['object_id', 'content_type']
                model_fields = fields_for_model(self.model).keys()
                fields = []
                # set.union() is not used for preserving order
                for field in model_fields + list(self.readonly_fields):
                    if field not in excluded_fields and field not in fields:
                        fields.append(field)
                return fields
        return self.readonly_fields
    
    def get_view_permission(self, opts):
        return 'view_%s' % opts.object_name.lower()
    
    def has_view_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to view the given Django 
        model instance.
        
        If `obj` is None, this should return True if the given request has
        permission to change *any* object of the given type.
        """
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + self.get_view_permission(opts), obj)
    
    def has_add_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to add an object.
        """
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_add_permission(), obj)
    
    def has_change_permission(self, request, obj=None, view=True):
        """
        WARN: Hacky version of has_change_permission
        Returns True if the given request has permission to view or change the given
        Django model instance.
        If view is set to False, then it will only return True if the user has change
        permission.
        """
        opts = self.opts
        # Hack to avoid copy&pasta all django's changelist_view and change_view
        if request.method == 'GET' and view:
            return self.has_view_permission(request, obj)
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission(), obj)
    
    def has_delete_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance.
        """
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission(), obj)
    
    def get_model_perms(self, request):
        """
        Returns a dict of all perms for this model. This dict has the keys
        ``add``, ``change``, and ``delete`` and ``view`` mapping to the True/False
        for each of those actions.
        ** Not sure for what is used **
        """
        return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
            'view': self.has_view_permission(request),
        }
    
    def save_model(self, request, obj, form, change):
        """ Passing obj to has_add_permission for checking """
        if not change and not self.has_add_permission(request, obj):
            raise PermissionDenied
        obj.save()
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """ update context has_change_permission with true change_permission """
        template_response = super(PermExtensionMixin, self).render_change_form(request,
            context, add=add, change=change, form_url=form_url, obj=obj)
        template_response.context_data['has_change_permission'] = self.has_change_permission(request, obj, view=False)
        return template_response

class PermissionModelAdmin(PermExtensionMixin, admin.ModelAdmin):
    pass


class PermissionTabularInline(PermExtensionMixin, admin.TabularInline):
    pass


class PermissionGenericTabularInline(PermExtensionMixin, generic.GenericTabularInline):
    pass

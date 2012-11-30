from django.contrib import admin
from django.contrib.contenttypes import generic
from django.core.exceptions import PermissionDenied
from django.forms.models import fields_for_model

from .helpers import change_view, changelist_view


class PermExtensionMixin(object):
    change_form_template = 'admin/permissions_change_form.html'
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make all fields read only if user doesn't have change permissions.
        """
        if not self.has_change_permission(request, obj=obj) and \
            self.has_view_permission(request, obj=obj):
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
    
    def has_add_permission(self, request):
        """
        Returns True if the given request has permission to add an object.
        Can be overriden by the user in subclasses.
        """
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_add_permission())
    
    def has_change_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.
        
        Can be overriden by the user in subclasses. In such case it should
        return True if the given request has permission to change the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to change *any* object of the given type.
        """
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission(), obj)
    
    def has_delete_permission(self, request, obj=None):
        """
        Returns True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.
        
        Can be overriden by the user in subclasses. In such case it should
        return True if the given request has permission to delete the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to delete *any* object of the given type.
        """
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission(), obj)
    
    def get_model_perms(self, request):
        """
        Returns a dict of all perms for this model. This dict has the keys
        ``add``, ``change``, and ``delete`` and ``view`` mapping to the True/False
        for each of those actions.
        """
        return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
            'view': self.has_view_permission(request),
        }
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        print 'permissions'
        if request.method == 'POST':
            # User is trying to save
            if not self.has_change_permission(request, None):
                raise PermissionDenied
        else:
            if not (self.has_change_permission(request, None) or self.has_view_permission(request, None)):
                raise PermissionDenied
        return change_view(self, request, object_id, form_url=form_url, extra_context=extra_context)
    
    def changelist_view(self, request, extra_context=None):
        if not (self.has_change_permission(request, None) or self.has_view_permission(request, None)):
            raise PermissionDenied
        return changelist_view(self, request, extra_context=extra_context)
    
    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        for inline_class in self.inlines:
            inline = inline_class(self.model, self.admin_site)
            if request:
                try: inline.has_view_permission(request)
                except AttributeError: continue
                if not (inline.has_view_permission(request) or
                        inline.has_add_permission(request) or
                        inline.has_change_permission(request, obj) or
                        inline.has_delete_permission(request, obj)):
                    continue
                if not inline.has_add_permission(request):
                    inline.max_num = 0
            inline_instances.append(inline)
        
        return inline_instances
    
    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be viewes or edited by the
        admin site. This is used by changelist_view and inline change_view.
        """
        qs = self.model._default_manager.get_query_set()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        if not (self.has_view_permission(request) or self.has_change_permission(request)):
            qs = qs.none()
        return qs


class PermissionModelAdmin(PermExtensionMixin, admin.ModelAdmin):
    pass

class PermissionTabularInline(PermExtensionMixin, admin.TabularInline): pass

class PermissionGenericTabularInline(PermExtensionMixin, generic.GenericTabularInline): pass

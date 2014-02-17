from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib.contenttypes import generic
from django.core.exceptions import PermissionDenied
from django.forms.models import fields_for_model
from django.utils.encoding import force_text


# WARNING: *HACKY MODULE*
# There are lots of hacks down there, mostly because avoiding Django code copypasta
# Note: Django admin doesn't check for inline permissions if they don't have modeladmin


# TODO: View permissions -> qset (define on permission._get_view_queryset())


class ReadPermModelAdminMixin(object):
    """ Mixing class that adds view permission support to ModelAdmin """
    change_form_template = 'admin/permissions_change_form.html'
    save_and_continue = False
    sudo_actions = []
    
    def get_readonly_fields(self, request, obj=None):
        """ Makes all fields read only if user doesn't have change permissions """
        if not self.has_change_permission(request, obj=obj, view=False):
            if self.has_view_permission(request, obj=obj):
                excluded_fields = ['object_id', 'content_type']
                model_fields = fields_for_model(self.model).keys()
                fields = []
                # more efficient set.union() is not used for preserving order
                for field in model_fields + list(self.readonly_fields):
                    if field not in excluded_fields and field not in fields:
                        fields.append(field)
                return fields
        return self.readonly_fields
    
    def get_actions(self, request):
        """ Exclude sudo actions for unprivileged users """
        actions = super(ReadPermModelAdminMixin, self).get_actions(request)
        if not request.user.is_superuser:
            for action in self.sudo_actions:
                name = action.func_name if callable(action) else action
                if name in actions:
                    del actions[name]
        return actions
    
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
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Change title to View object if user has read only """
        opts = self.model._meta
        obj = self.get_object(request, unquote(object_id))
        context = {}
        if not self.has_change_permission(request, obj, view=False):
            model = force_text(opts.verbose_name)
            context = {'title': 'View %s %s' % (model, obj)} 
        context.update(extra_context or {})
        return super(ReadPermModelAdminMixin, self).change_view(request, object_id,
            form_url='', extra_context=context)
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """ update context has_change_permission with true change_permission """
        template_response = super(ReadPermModelAdminMixin, self).render_change_form(request,
            context, add=add, change=change, form_url=form_url, obj=obj)
        has_change_permission = self.has_change_permission(request, obj, view=False)
        template_response.context_data['has_change_permission'] = has_change_permission
        template_response.context_data['save_and_continue'] = self.save_and_continue
        return template_response
    
    def get_inline_instances(self, request, obj=None):
        """ Hack! Hook parent obj just in time to use in inline has_add_permission """
        request.__parent_object__ = obj
        return super(ReadPermModelAdminMixin, self).get_inline_instances(request, obj=obj)


class PermissionModelAdmin(ReadPermModelAdminMixin, admin.ModelAdmin):
    """ Base class for supporting permissions on ModelAdmins """


class ReadPermInlineModelAdminMixin(ReadPermModelAdminMixin):
    def has_add_permission(self, request, obj=None):
        """ Prevent add another button to appear """
        opts = self.opts
        parent = request.__parent_object__
        if parent is not None:
            if not request.user.has_perm(opts.app_label + '.' + opts.get_change_permission(), parent):
                return False
                # TODO inlines save_model is not called so we have find the way 
                #      of checking add permissions with the resulting object, shall we?
        return super(ReadPermInlineModelAdminMixin, self).has_add_permission(request, obj=obj)


class PermissionStackedInline(ReadPermInlineModelAdminMixin, admin.StackedInline):
    """ Base class for supporting permissions on StackedInlines """


class PermissionTabularInline(ReadPermInlineModelAdminMixin, admin.TabularInline):
    """ Base class for supporting permissions on TabularInlines """


class PermissionGenericTabularInline(ReadPermInlineModelAdminMixin, generic.GenericTabularInline):
    """ Base class for supporting permissions on GenericTabularInlines """

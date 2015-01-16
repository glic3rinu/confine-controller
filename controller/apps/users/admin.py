from __future__ import absolute_import

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, resolve
from django.db import models
from django.utils.safestring import mark_safe

from controller.admin import ChangeViewActions, SortableTabularInline
from controller.admin.utils import get_admin_link
from controller.utils.apps import is_installed
from permissions.admin import PermissionModelAdmin, PermissionTabularInline

from .actions import join_request, enable_account, send_email
from .filters import MyGroupsListFilter
from .forms import (UserCreationForm, UserChangeForm, GroupRolesFormSet,
    UserRolesForm, JoinRequestForm, GroupAdminForm, GroupRolesInlineForm)
from .models import User, AuthToken, Roles, Group, JoinRequest, ResourceRequest

if is_installed('registration'):
    from .registration import admin as reg_admin # overrides registration.admin


class AuthTokenInline(PermissionTabularInline):
    model = AuthToken
    extra = 0
    
    class Media:
        css = {
             'all': ('users/monospace-authtoken.css',)
        }
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Use monospace font style in script textarea """
        if db_field.name == 'data':
            kwargs['widget'] = forms.Textarea(
                attrs={'cols': 130, 'rows': '6'})
        return super(AuthTokenInline, self).formfield_for_dbfield(db_field, **kwargs)


class GroupRolesInline(PermissionTabularInline, SortableTabularInline):
    model = Roles
    extra = 0
    formset = GroupRolesFormSet
    form = GroupRolesInlineForm
    sortable_fields = {'user': 'user__name'}
    verbose_name = 'member'
    verbose_name_plural = 'members'
    
    class Media:
        css = { 'all': ('controller/css/hide-inline-id.css',) }
    
    def get_formset(self, request, obj=None, **kwargs):
        """
        Hook obj into formset to tell the difference bewteen add or change so it
        can validate correctly that each group has at least one admin, except
        during the add process which will be added automatically
        """
        self.formset.group = obj
        self.form.group = obj
        return super(GroupRolesInline, self).get_formset(request, obj=obj, **kwargs)
    
    def has_add_permission(self, request):
        """ Disable add roles when adding a new group """
        if resolve(request.path).url_name == 'users_group_add':
            return False
        return super(GroupRolesInline, self).has_add_permission(request)


class UserRolesInline(PermissionTabularInline):
    fields = ['group_link', 'group', 'is_group_admin', 'is_node_admin', 'is_slice_admin']
    readonly_fields = ['group_link', 'group', 'is_group_admin', 'is_node_admin', 'is_slice_admin']
    model = Roles
    extra = 0
    form = UserRolesForm
    
    def group_link(self, instance):
        """ Link to related Group """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.group))
    group_link.short_description = 'Group'
    
    def get_fieldsets(self, request, obj=None):
        """ HACK display message using the field name of the inline form """
        name = 'Roles'
        if obj is not None:
            if self.has_change_permission(request, obj, view=False):
                groups_url = reverse('admin:users_group_changelist')
                name = 'Roles <a href="%s">(Request group membership)</a>' % groups_url
        self.verbose_name_plural = mark_safe(name)
        fieldsets = super(UserRolesInline, self).get_fieldsets(request, obj=obj)
        fields = list(fieldsets[0][1]['fields'])
        if request.user.is_superuser:
            fields.remove('group_link')
        else:
            fields.remove('group')
        fieldsets[0][1]['fields'] = fields
        return fieldsets
    
    def get_readonly_fields(self, request, obj=None):
        """ Makes all fields read only if user doesn't have change permissions """
        fields = super(UserRolesInline, self).get_readonly_fields(request, obj)
        if request.user.is_superuser:
            return ['group_link']
        return fields
    
    def has_add_permission(self, request, **kwargs):
        return request.user.is_superuser


class JoinRequestInline(PermissionTabularInline):
    fields = ('user_link', 'roles', 'action')
    readonly_fields = ('user_link',)
    model = JoinRequest
    extra = 0
    form = JoinRequestForm
    can_delete = False
    
    def has_add_permission(self, request):
        return False
    
    def user_link(self, instance):
        """ Link to related User """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.user))
    user_link.short_description = 'User'
    
    def get_formset(self, request, obj=None, **kwargs):
        """ Hook request for future usage in the inline form """
        self.form.__request__ = request
        return super(JoinRequestInline, self).get_formset(request, obj=obj, **kwargs)


class UserAdmin(AuthUserAdmin, PermissionModelAdmin):
    list_display = (
        'name', 'email', 'group_links', 'is_superuser', 'is_active'
    )
    list_filter = (
        'is_active', 'is_superuser', 'roles__is_group_admin', 'roles__is_slice_admin',
        'roles__is_node_admin', 'groups'
    )
    fieldsets = (
        (None, {'fields': ('username', )}),
        ('Personal info', {'fields': ('name', 'email', 'description',)}),
        ('Permissions', {'fields': ('is_active', 'is_superuser',)}),
        ('Important dates', {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2',), 'classes': ('wide',)}),
        ('Personal info', {'fields': ('name', 'email',), 'classes': ('wide',)}),
    )
    
    search_fields = ('username', 'email', 'name')
    ordering = ('name',)
    inlines = [AuthTokenInline, UserRolesInline]
    actions = [enable_account, send_email]
    sudo_actions = ['delete_selected', 'enable_account', 'send_email']
    filter_horizontal = ()
    form = UserChangeForm
    add_form = UserCreationForm
    
    def group_links(self, instance):
        groups = instance.groups.all()
        return ', '.join([ get_admin_link(group) for group in groups ])
    group_links.allow_tags = True
    group_links.short_description = 'Groups'
    
    def get_readonly_fields(self, request, obj=None):
        """ Makes all fields read only if user doesn't have change permissions """
        fields = super(UserAdmin, self).get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            fields += ('last_login', 'date_joined', 'is_active', 'is_superuser')
        return fields
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make description input widget smaller """
        if db_field.name == 'description':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 85, 'rows': 5})
        return super(UserAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def get_inline_instances(self, request, obj=None):
        """ show/hide inlines depending if is a new obj """
        inlines = super(UserAdmin, self).get_inline_instances(request, obj=obj)
        if obj is None:
            # Remove roles inline
            return inlines[:1]
        return inlines

    def user_change_password(self, request, id, form_url=''):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super(UserAdmin, self).user_change_password(request, id, form_url=form_url)


class GroupAdmin(ChangeViewActions, PermissionModelAdmin):
    list_display = [
        'name', 'description', 'allow_nodes_info', 'allow_slices_info', 'num_users'
    ]
    list_filter = [MyGroupsListFilter, 'allow_slices', 'allow_nodes']
    search_fields = ['name', 'description']
    inlines = [GroupRolesInline, JoinRequestInline]
    actions = [join_request]
    change_view_actions = [join_request]
    change_form_template = 'admin/users/group/change_form.html'
    form = GroupAdminForm
    save_and_continue = True
    
    def get_form(self, request, obj=None, **kwargs):
        """ Decides whether to show allow_resource or request_resource"""
        form = super(GroupAdmin, self).get_form(request, obj=obj, **kwargs)
        readonly_fields = self.get_readonly_fields(request, obj=obj)
        user = request.user
        for resource, verbose in ResourceRequest.RESOURCES:
            if user.is_superuser or 'allow_%s' % resource in readonly_fields:
                form.base_fields.pop('request_%s' % resource)
            else:
                form.base_fields.pop('allow_%s' % resource, None)
        # Hook request for sending emails on form.save
        form.__request__ = request
        return form
    
    def get_inline_instances(self, request, obj=None):
        """ show/hide inlines depending on user permissions and is a new obj """
        inlines = super(GroupAdmin, self).get_inline_instances(request, obj=obj)
        if obj is None:
            return [] 
        elif self.has_change_permission(request, obj, view=False):
            return inlines
        else:
            # remove JoinRequestInline
            return inlines[:1] 

    def get_readonly_fields(self, request, obj=None):
        """ Make allow_resource readonly accordingly """
        fields = super(GroupAdmin, self).get_readonly_fields(request, obj=obj)
        if not request.user.is_superuser and obj is not None:
            for resource, verbose in ResourceRequest.RESOURCES:
                resource = 'allow_%s' % resource
                if getattr(obj, resource) and resource not in fields:
                    fields += (resource,)
        return fields
    
    def allow_nodes_info(self, instance):
        """Change allow nodes if exists a resource request"""
        if instance.resource_requests.filter(resource='nodes').exists():
            return None
        return instance.allow_nodes
    allow_nodes_info.boolean = True
    allow_nodes_info.short_description = "Allow nodes"
    
    def allow_slices_info(self, instance):
        """Change allow slices if exists a resource request"""
        if instance.resource_requests.filter(resource='slices').exists():
            return None
        return instance.allow_slices
    allow_slices_info.boolean = True
    allow_slices_info.short_description = "Allow slices"
    
    def num_users(self, instance):
        """ return num users as a link to users changelist view """
        num = instance.users.count()
        url = reverse('admin:users_user_changelist')
        url += '?groups=%s' % instance.pk
        return mark_safe('<a href="%s">%d</a>' % (url, num))
    num_users.short_description = 'Users'
    num_users.admin_order_field = 'users__count'
    
    def save_model(self, request, obj, form, change):
        """ user that creates a group becomes its admin """
        super(GroupAdmin, self).save_model(request, obj, form, change)
        if not change:
            Roles.objects.get_or_create(user=request.user, group=obj, is_group_admin=True)
    
    def get_queryset(self, request):
        """ Annotate number of users on the slice for sorting on changelist """
        qs = super(GroupAdmin, self).get_queryset(request)
        qs = qs.annotate(models.Count('users'))
        return qs


class RolesAdmin(admin.ModelAdmin):
    list_display = [
        'user_query_string', 'group_link', 'is_group_admin', 'is_node_admin', 'is_slice_admin'
    ]
    list_editable = ['is_group_admin', 'is_node_admin', 'is_slice_admin']
    list_filter = ['is_group_admin', 'is_node_admin', 'is_slice_admin', 'group']
    
    def group_link(self, instance):
        """ Link to related Group """
        return get_admin_link(instance.group)
    group_link.short_description = 'Group'
    group_link.admin_order_field = 'group'
    
    def user_query_string(self, instance):
        query_string = '?'+self.__request__.META['QUERY_STRING']
        url = reverse('admin:users_roles_change', args=[instance.pk])+query_string
        return mark_safe('<a href="%s">%s</a>' % (url, instance.user))
    user_query_string.short_description = 'User'
    user_query_string.admin_order_field = 'user'
    
    def changelist_view(self, request, *args, **kwargs):
        """ hook request for use in user_query_string """
        self.__request__ = request
        return super(RolesAdmin, self).changelist_view(request, *args, **kwargs)
    
    def _preserve_query_string(self, request, response):
        query_string = '?' + request.META['QUERY_STRING']
        location = response._headers['location']
        response._headers['location'] = (location[0], location[1]+query_string)
        return response
    
    def get_queryset(self, request):
        related = ('user', 'group')
        return super(RolesAdmin, self).get_queryset(request).select_related(*related)
    
    def response_add(self, request, *args, **kwargs):
        response = super(RolesAdmin, self).response_add(request, *args, **kwargs)
        return self._preserve_query_string(request, response)
    
    def response_change(self, request, obj):
        response = super(RolesAdmin, self).response_change(request, obj)
        return self._preserve_query_string(request, response)
    
    def response_action(self, request, queryset):
        response = super(RolesAdmin, self).response_action(request, queryset)
        return response


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Roles, RolesAdmin)
admin.site.unregister(AuthGroup)

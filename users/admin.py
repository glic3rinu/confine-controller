from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError, transaction
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from common.admin import link, get_admin_link, ChangeViewActionsModelAdmin
from permissions.admin import PermissionModelAdmin, PermissionTabularInline

from .actions import join_request
from .forms import UserCreationForm, UserChangeForm, JoinRequestForm
from .models import User, AuthToken, Roles, Group, JoinRequest


class AuthTokenInline(PermissionTabularInline):
    model = AuthToken
    extra = 0


class RolesInline(PermissionTabularInline):
    model = Roles
    extra = 0


class JoinRequestInline(PermissionTabularInline):
    model = JoinRequest
    extra = 0
    fields = ('user_link', 'action', 'roles')
    readonly_fields = ('user_link',)
    form = JoinRequestForm
    
    def has_add_permission(self, request):
        return False
    
    def user_link(self, instance):
        """ Link to related User """
        return mark_safe("<b>%s</b>" % get_admin_link(instance.user))
    user_link.short_description = 'User'


class UserAdmin(UserAdmin, PermissionModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 
                    'group_links', 'is_superuser', 'is_active', )
    list_filter = ('is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email',
                                      'description',)}),
        ('Permissions', {'fields': ('is_active', 'is_superuser',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email')}
        ),)
    
    search_fields = ('username', 'email', 'first_name', 'last_name')
    inlines = [AuthTokenInline, RolesInline]
    filter_horizontal = ()
    form = UserChangeForm
    add_form = UserCreationForm
    
    def group_links(self, instance):
        groups = instance.groups.all()
        return ', '.join([ get_admin_link(group) for group in groups ])
    group_links.allow_tags = True
    group_links.short_description = 'Groups'


class GroupAdmin(ChangeViewActionsModelAdmin, PermissionModelAdmin):
    list_display = ['name', 'description', 'allow_slices', 'allow_nodes',
                    'num_users']
    list_filter = ['allow_slices', 'allow_nodes']
    search_fields = ['name', 'description']
    inlines = [RolesInline, JoinRequestInline]
    # TODO this is redundant if is_approved is deprecated
    fields = ('name', 'description', 'allow_nodes', 'allow_slices')
    actions = [join_request]
    change_view_actions = [('join-request', join_request, 'Join request', ''),]
    change_form_template = 'admin/users/group/change_form.html'
    
    def num_users(self, instance):
        return instance.user_set.all().count()
    num_users.short_description = 'Users'
    num_users.admin_order_field = 'user__count'
    
    def queryset(self, request):
        """ 
        Annotate number of users on the slice for sorting on changelist 
        """
        qs = super(GroupAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('user'))
        return qs


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.unregister(AuthGroup)


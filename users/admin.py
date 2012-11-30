from __future__ import absolute_import

from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms.widgets import CheckboxSelectMultiple

from common.admin import link, admin_link
from permissions.admin import PermissionModelAdmin, PermissionTabularInline

from .forms import UserCreationForm, UserChangeForm
from .models import User, AuthToken, Roles, Group


class AuthTokenInline(PermissionTabularInline):
    model = AuthToken
    extra = 0


class RolesInline(PermissionTabularInline):
    model = Roles
    extra = 0


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
        ('SFA Options', {'classes': ('collapse',), 'fields': ('uuid', 'pubkey')}),
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
        return ', '.join([admin_link('')(group) for group in groups])
    group_links.allow_tags = True
    group_links.short_description = 'Groups'


class GroupAdmin(PermissionModelAdmin):
    list_display = ['name', 'uuid', 'description', 'allow_slices', 'allow_nodes',
                    'num_users']
    list_filter = ['allow_slices', 'allow_nodes']
    search_fields = ['name', 'description']
    inlines = [RolesInline]
    fieldsets = (
        (None, {'fields': ('name', 'description', 'allow_nodes', 'allow_slices')}),
        ('SFA Options', {'classes': ('collapse',), 'fields': ('uuid', 'pubkey')}),
        )
    
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


from __future__ import absolute_import

from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.admin import UserAdmin
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
    list_display = ['name', 'uuid', 'description', 'allow_slices', 'allow_nodes']
    list_filter = ['allow_slices', 'allow_nodes']
    search_fields = ['name', 'description']
    fieldsets = (
        (None, {'fields': ('name', 'description', 'allow_nodes', 'allow_slices')}),
        ('SFA Options', {'classes': ('collapse',), 'fields': ('uuid', 'pubkey')}),
        )

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.unregister(AuthGroup)


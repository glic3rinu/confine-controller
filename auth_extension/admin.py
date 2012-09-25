from common.admin import insert_inline
from common.fields import MultiSelectFormField
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from models import UserProfile, AuthToken, ResearchGroup, TestbedPermission, AuthorizedOfficial


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 0


class AuthTokenInline(admin.TabularInline):
    model = AuthToken
    extra = 0


class TestbedPermissionInline(admin.TabularInline):
    model = TestbedPermission
    extra = 0


class AuthorizedOfficialInline(admin.StackedInline):
    model = AuthorizedOfficial


def action(testbdepermission):
    return str(testbdepermission.action)


class TestbedPermissionAdmin(admin.ModelAdmin):
    list_display = (action, 'user', 'research_group', 'node', 'slice')


class ResearchGroupAdmin(admin.ModelAdmin):
    inlines = [AuthorizedOfficialInline, TestbedPermissionInline]


insert_inline(User, UserProfileInline)
insert_inline(User, AuthTokenInline)
insert_inline(User, TestbedPermissionInline)

admin.site.register(ResearchGroup, ResearchGroupAdmin)
admin.site.register(TestbedPermission, TestbedPermissionAdmin)
admin.site.register(AuthorizedOfficial)

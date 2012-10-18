from auth_extension.models import (UserProfile, AuthToken, ResearchGroup, 
    TestbedPermission, AuthorizedOfficial)
from auth_extension.forms import UserProfileChangeForm
from common.admin import insert_inline, AddOrChangeInlineFormMixin
from django.contrib import admin
from django.contrib.auth.models import User


class UserProfileInline(admin.StackedInline, AddOrChangeInlineFormMixin):
    model = UserProfile
    max_num = 0
    change_form = UserProfileChangeForm


class AuthTokenInline(admin.TabularInline):
    model = AuthToken
    extra = 0


class TestbedPermissionInline(admin.TabularInline):
    model = TestbedPermission
    extra = 0


class AuthorizedOfficialInline(admin.StackedInline):
    model = AuthorizedOfficial


class TestbedPermissionAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'research_group', 'node', 'slice')
    
    def action(self, instance):
        return str(instance.action)


class ResearchGroupAdmin(admin.ModelAdmin):
    inlines = [AuthorizedOfficialInline, TestbedPermissionInline]


admin.site.register(ResearchGroup, ResearchGroupAdmin)
admin.site.register(TestbedPermission, TestbedPermissionAdmin)
admin.site.register(AuthorizedOfficial)


# Monkey-Patching Section

insert_inline(User, UserProfileInline)
insert_inline(User, AuthTokenInline)
insert_inline(User, TestbedPermissionInline)

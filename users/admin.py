from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.forms.widgets import CheckboxSelectMultiple

from users.forms import UserCreationForm, UserChangeForm
from users.models import (User, AuthToken, Role, Permission, ResearchGroup,
    UserResearchGroup)


class AuthTokenInline(admin.TabularInline):
    model = AuthToken
    extra = 0


class UserResearchGroupInline(admin.TabularInline):
    model = UserResearchGroup
    extra = 0
    verbose_name_plural = 'Research Groups'
    
    def get_formset(self, *args, **kwargs):
        """ Change default M2M widget for CheckboxSelectMultiple """
        formset = super(UserResearchGroupInline, self).get_formset(*args, **kwargs)
        formset.form.base_fields['roles'].widget = CheckboxSelectMultiple()
        return formset


class RoleAdmin(admin.ModelAdmin):
    filter_horizontal = ['permissions']


class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_superuser',
                    'is_active', )
    list_filter = ('is_superuser', 'is_active', 'research_groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone',
                                      'description',)}),
        ('Permissions', {'fields': ('is_active', 'is_superuser',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('SFA Options', {'classes': ('collapse',), 'fields': ('uuid', 'pubkey')}),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
        ),)
    
    search_fields = ('username', 'email', 'first_name', 'last_name')
    inlines = [AuthTokenInline, UserResearchGroupInline]
    filter_horizontal = ()
    form = UserChangeForm
    add_form = UserCreationForm


admin.site.register(Permission)
admin.site.register(ResearchGroup)
admin.site.register(Role, RoleAdmin)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)


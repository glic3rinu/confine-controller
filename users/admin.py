from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.admin import UserAdmin
from django.forms.widgets import CheckboxSelectMultiple

from common.admin import link, admin_link

from .forms import UserCreationForm, UserChangeForm
from .models import User, AuthToken, Roles, Group


class AuthTokenInline(admin.TabularInline):
    model = AuthToken
    extra = 0


class RolesInline(admin.TabularInline):
    model = Roles
    extra = 0
    
#    def get_formset(self, *args, **kwargs):
#        """ 
#        Change default M2M widget for CheckboxSelectMultiple
#        """
#        formset = super(RolesInline, self).get_formset(*args, **kwargs)
#        formset.form.base_fields['roles'].widget = CheckboxSelectMultiple()
#        return formset


class UserAdmin(UserAdmin):
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


class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'uuid', 'description']


admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.unregister(AuthGroup)


from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.forms.widgets import CheckboxSelectMultiple

from common.admin import link, admin_link

from .forms import UserCreationForm, UserChangeForm
from .models import User, AuthToken, Role, Permission, ResearchGroup, UserResearchGroup


class AuthTokenInline(admin.TabularInline):
    model = AuthToken
    extra = 0


class UserResearchGroupInline(admin.TabularInline):
    model = UserResearchGroup
    extra = 0
    verbose_name_plural = 'Research Groups'
    
    def get_formset(self, *args, **kwargs):
        """ 
        Change default M2M widget for CheckboxSelectMultiple and provide help_text 
        """
        formset = super(UserResearchGroupInline, self).get_formset(*args, **kwargs)
        formset.form.base_fields['roles'].widget = CheckboxSelectMultiple()
        help_text = ''
        for role in formset.form.base_fields['roles'].queryset.all():
            help_text += '%s: %s \n' % (role.name, role.description)
        formset.form.base_fields['roles'].help_text = help_text[:-1]
        return formset


class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 
                    'research_group_links', 'is_superuser', 'is_active', )
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
    
    def research_group_links(self, instance):
        groups = instance.research_groups.all()
        return ', '.join([admin_link('')(group) for group in groups])
    research_group_links.allow_tags = True
    research_group_links.short_description = 'Research Groups'


class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    filter_horizontal = ['permissions']


class ResearchGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', link('url')]
    list_filter = ['country']


class PermissionAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'content_type', 'action', 'eval', 'eval_description']
    list_filter = ['action', 'content_type']


admin.site.register(Permission, PermissionAdmin)
admin.site.register(ResearchGroup, ResearchGroupAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)


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
from .forms import UserCreationForm, UserChangeForm
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
    readonly_fields = ('user', 'action_links')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def action_links(self, instance):
        actions = ['accept', 'refuse']
        # kwargs pel reverse()
        kwargs = {'group_id': instance.group_id, 'request_id': instance.id}
        urls = [ reverse('admin:%s_join_request' % a, kwargs=kwargs) for a in actions ]
        hrefs = [ '<a href="%s">[%s]</a>' % (url, a) for (url, a) in zip(urls, actions) ]
        return mark_safe(' '.join(hrefs))
    action_links.short_description = 'actions'

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
    fieldsets = (
        (None, {'fields': ('name', 'description', 'allow_nodes', 'allow_slices')}),
        )
    actions = [join_request]
    change_view_actions = [('join-request', join_request, 'Join request', ''),]
    change_form_template = 'admin/common/change_form.html'

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

    def get_urls(self):
        urls = super(GroupAdmin, self).get_urls()
        actions_urls = patterns('',
            url(r'^(?P<group_id>\d+)/accept-join-request/(?P<request_id>\d+)$',
                self.admin_site.admin_view(self.accept_join_request_view),
                name='accept_join_request'),
            url(r'^(?P<group_id>\d+)/refuse-join-request/(?P<request_id>\d+)$',
                self.admin_site.admin_view(self.refuse_join_request_view),
                name='refuse_join_request'),
        )
        return actions_urls + urls

    @transaction.commit_on_success
    def accept_join_request_view(self, request, group_id, request_id):
        """
        Accept join request
        """
        jrequest = JoinRequest.objects.get(pk=request_id)
        # we can reuse the group_change permission
        if not request.user.has_perm('users.group_change', obj=jrequest):
            raise PermissionDenied

        jrequest.accept()
        messages.info(request, "User %s has been added to the group" % jrequest.user)
        return HttpResponseRedirect(reverse('admin:users_group_change', args=[group_id]))

    @transaction.commit_on_success
    def refuse_join_request_view(self, request, group_id, request_id):
        """
        Refuse join request
        """
        jrequest = JoinRequest.objects.get(pk=request_id)
        if not request.user.has_perm('users.group_change', obj=jrequest):
            raise PermissionDenied

        jrequest.refuse()
        messages.info(request, "Join refused for user %s" % jrequest.user)
        return HttpResponseRedirect(reverse('admin:users_group_change', args=[group_id]))

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.unregister(AuthGroup)


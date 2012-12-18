from __future__ import absolute_import

from django.contrib import admin, messages
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError, transaction
from django.http import Http404
from django.shortcuts import redirect
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from common.admin import link, admin_link
from permissions.admin import PermissionModelAdmin, PermissionTabularInline

from .forms import UserCreationForm, UserChangeForm
from .models import User, AuthToken, Roles, Group, JoinRequest


class AuthTokenInline(PermissionTabularInline):
    model = AuthToken
    extra = 0


class RolesInline(PermissionTabularInline):
    model = Roles
    extra = 0

def action_link(instance, action):
    #/admin/users/group/{group_id}/join_[action]/?id=[joinReq_id]
    url = reverse('admin:users_group_join_%s' % action, args=(instance.group.id,))
    url = url + "?id=%s" % instance.id
    href_name = action
    return mark_safe(' <a href="%s">[%s]</a> ' % (url, href_name))

def actions(instance):
    act_accept = action_link(instance, "accept")
    act_refuse = action_link(instance, "refuse")
    
    return act_accept + act_refuse

class JoinRequestInline(PermissionTabularInline):
    model = JoinRequest
    extra = 0
    readonly_fields = ('user', actions)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

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
    inlines = [RolesInline, JoinRequestInline]
    fieldsets = (
        (None, {'fields': ('name', 'description', 'allow_nodes', 'allow_slices')}),
        ('SFA Options', {'classes': ('collapse',), 'fields': ('uuid', 'pubkey')}),
        )
    actions = ['join_request']
    change_form_template = 'admin/group_change_form.html'

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

    def join_request(self, request, queryset):
        """
        @action
        The user can create request to join some groups.
        If there are any error when creating a request, the process continues
        for the other groups.

        """
        for group in queryset:
            self._new_join_request(request, group)

    join_request.short_description = "Request to join the groups selected"

    def get_urls(self):
        from django.conf.urls import patterns, url
        urls = super(GroupAdmin, self).get_urls()
        actions_urls = patterns('',
            url(r'^(?P<group_id>\d)/join/$', self.admin_site.admin_view(self.join_request_view), name='users_group_join'),
            url(r'^(?P<group_id>\d)/join_accept/$', self.admin_site.admin_view(self.join_accept_view), name='users_group_join_accept'),
            url(r'^(?P<group_id>\d)/join_refuse/$', self.admin_site.admin_view(self.join_refuse_view), name='users_group_join_refuse'),
        )
        return actions_urls + urls

    def join_request_view(self, request, group_id):
        """
        Create a join request in the group "group_id" view

        """
        group = Group.objects.get(pk=group_id)
        self._new_join_request(request, group)

        return redirect('admin:users_group_change', group_id)

    def join_accept_view(self, request, group_id):
        """
        Accept a join request

        """
        jreq_id = request.GET.get('id', False)
        if not jreq_id:
            messages.error(request, "Invalid request")

        if self.__has_join_change_permissions(request, group_id):
            try:
                jreq = JoinRequest.objects.get(pk=jreq_id)
            except JoinRequest.DoesNotExist:
                raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': 'JoinRequest', 'key': escape(jreq_id)})
            jreq.accept()
            messages.info(request, "User %s has been added to the group" % jreq.user)
        else:
            messages.error(request, "Insufficient privileges")
            raise PermissionDenied

        return redirect('admin:users_group_change', group_id)

    def join_refuse_view(self, request, group_id):
        """
        Refuse a join request

        """
        if not request.GET.__contains__('id'):
            messages.error(request, "Invalid request")

        if self.__has_join_change_permissions(request, group_id):
            jreq = JoinRequest.objects.get(pk=request.GET['id'])
            jreq.refuse()
            messages.info(request, "Join refused for user %s" % jreq.user)
        else:
            messages.error(request, "Insufficient privileges")
        
        return redirect('admin:users_group_change', group_id)

    def __has_join_change_permissions(self, request, group_id):
        #TODO: implement as permissions.py??
        group = Group.objects.get(pk=group_id)
        if request.user.is_superuser:
            return True
        if not group.has_role(request.user, 'admin'):
            return False
        
        return True

    def _new_join_request(self, request, group):
        """
        Try to create a new JoinRequest. If there are any problem (e.g. alreday
        exists a join request for this user into this group); it shows a message
        otherwise it instantiates the request.

        """
        try:
            sid = transaction.savepoint()
            JoinRequest.objects.create(user=request.user, group=group)
            transaction.savepoint_commit(sid)
            messages.success(request, "Your join request has been sent (%s)" % group)
        except IntegrityError:
            transaction.savepoint_rollback(sid)
            messages.error(request, "You have alreday sent a request to this group (%s)" % group)

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.unregister(AuthGroup)


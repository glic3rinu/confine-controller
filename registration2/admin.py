from common.admin import action_to_view, admin_link, ChangeViewActionsModelAdmin

from django.conf.urls import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from registration2.actions import approve_group, reject_group
from registration2.models import GroupRegistration

class GroupRegistrationAdmin(ChangeViewActionsModelAdmin):
    actions = [approve_group, reject_group]
    change_form_template = "admin/registration2/groupregistration/change_form.html"
    change_view_actions = [('approve', approve_group, '', ''),
                           ('reject', reject_group, '', '')]

    list_display = ('date', admin_link('group'), admin_link('user'))
    list_display_links = []
    readonly_fields = ('group', 'user', 'date')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(GroupRegistration, GroupRegistrationAdmin) 

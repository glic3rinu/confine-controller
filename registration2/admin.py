from common.admin import action_to_view, admin_link, ChangeViewActionsModelAdmin

from django.conf.urls import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils.safestring import mark_safe

from registration2.models import GroupRegistration

class GroupRegistrationAdmin(ChangeViewActionsModelAdmin):
    actions = ['approve_group', 'reject_group']
    change_form_template = "admin/registration2/groupregistration/change_form.html"
    change_view_actions = [('approve', 'approve_group', '', ''),
                           ('reject', 'reject_group', '', '')]

    list_display = ('date', admin_link('group'), admin_link('user'))
    list_display_links = []
    readonly_fields = ('group', 'user', 'date')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


    def get_urls(self):
        """ Hook group registration management URLs on group
        registration admin """
        urls = super(GroupRegistrationAdmin, self).get_urls()
        admin_site = self.admin_site
        extra_urls = patterns('',
            url(r'^(P<gr_id>\d+)/approve_group/$',
                admin_site.admin_view(self.approve_group_view),
                name='approve_group'),
            url(r'^(P<gr_id>\d+)/reject_group/$',
                admin_site.admin_view(self.reject_group_view),
                name='reject_group')
        )
        return extra_urls + urls

    ### VIEWS
    def approve_group_view(self, request, rgroup_id):
        return action_to_view(self.approve_group, GroupRegistrationAdmin)
    
    def reject_group_view(self, request, rgroup_id):
        return redirect('admin:registration2_groupregistration_changelist')

    ### move to actions
    @transaction.commit_on_success
    def approve_group(self, request, queryset):
        rows_updated = 0
        for group in queryset:
            group.approve()
            rows_updated+=1
            
        self.message_user(request, "%s group(s) has been approved" % rows_updated)

    approve_group.short_description = "Approve selected groups"

    @transaction.commit_on_success
    def reject_group(self, request, queryset):
        for group in queryset:
            group.reject()

        rows_updated = queryset.delete()
        self.message_user(request, "%s group(s) has been rejected" % rows_updated)

    reject_group.short_description = "Reject selected groups"

admin.site.register(GroupRegistration, GroupRegistrationAdmin) 

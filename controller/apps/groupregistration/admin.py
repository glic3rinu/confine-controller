from django.contrib import admin

from controller.admin import ChangeViewActions
from controller.admin.utils import (insert_list_display, insert_action)

from users.admin import GroupAdmin
from users.models import Group

from groupregistration.actions import approve_group, reject_group
from groupregistration.models import GroupRegistration


def group_info(obj):
    return ''.join([
                display_field('Name', obj.group.name),
                display_field('Description', obj.group.description),
            ])


def user_info(obj):
    return ''.join([
                display_field('username', obj.user.username),
                display_field('email', obj.user.email),
            ])


def display_field(name, value):
    return "<strong>%s:</strong> %s<br/>" % (name, value)


group_info.allow_tags = True
user_info.allow_tags = True


class GroupRegistrationAdmin(ChangeViewActions):
    actions = [approve_group, reject_group]
    change_view_actions = [('approve', approve_group, '', ''),
                           ('reject', reject_group, '', '')]

    list_display = (group_info, user_info)
    readonly_fields = ('group', 'user', 'date')

    # Disable delete from actions menu
    def get_actions(self, request):
        actions = super(GroupRegistrationAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # hack for not link with change_form view
    # http://stackoverflow.com/a/3999436/1538221
    def __init__(self,*args,**kwargs):
        super(GroupRegistrationAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

#admin.site.register(GroupRegistration, GroupRegistrationAdmin)


# Monkey Patch section

def is_approved(group):
    return GroupRegistration.is_group_approved(group.pk)
is_approved.boolean = True


insert_list_display(GroupAdmin, is_approved)
insert_action(Group, approve_group)
insert_action(Group, reject_group)

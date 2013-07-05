from StringIO import StringIO 

from django.db import transaction
from django.core.management import call_command

from .tasks import notify


def run_notifications(modeladmin, request, queryset):
    ids = queryset.values_list('pk', flat=True)
    notify(ids=ids)
    msg = '%i notifications had been executed' % len(ids)
    modeladmin.message_user(request, msg)


def upgrade_notifications(modeladmin, request, queryset):
    for num, notification in enumerate(queryset):
        notification.subject = notification.instance.default_subject
        notification.message = notification.instance.default_message
        notification.save()
    msg = '%i notifications had been upgraded' % (num+1)
    modeladmin.message_user(request, msg)
upgrade_notifications.description = ('Override current subject and message for '
    'the one provided by default')
upgrade_notifications.short_description = 'Upgrade subject and message'


@transaction.commit_on_success
def sync_notifications(modeladmin, request, queryset):
    content = StringIO()
    call_command('syncnotifications', stdout=content)
    content.seek(0)
    found = [line.split(' ')[1] for line in content.read().splitlines()]
    msg = '%i notifications had been found (%s)' % (len(found), ', '.join(found))
    modeladmin.message_user(request, msg)
sync_notifications.description = "Syncronize existing notifications with the database"


@transaction.commit_on_success
def enable_selected(modeladmin, request, queryset):
    queryset.update(is_active=True)
    msg = 'Selected %i notifications had been enabled' % queryset.count()
    modeladmin.message_user(request, msg)
enable_selected.description = "Enable selected notifications"
enable_selected.short_description = "Enable selected notifications"


@transaction.commit_on_success
def disable_selected(modeladmin, request, queryset):
    queryset.update(is_active=False)
    msg = 'Selected %i notifications had been disabled' % queryset.count()
    modeladmin.message_user(request, msg)
disable_selected.description = "Disable selected notifications"
disable_selected.short_description = "Disable selected notifications"


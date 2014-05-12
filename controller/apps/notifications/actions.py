from django.db import transaction

from controller.utils.plugins.actions import sync_plugins_action

from .tasks import notify


def run_notifications(modeladmin, request, queryset):
    ids = queryset.values_list('pk', flat=True)
    notify(ids=ids)
    msg = '%i notifications have been executed.' % len(ids)
    modeladmin.message_user(request, msg)
run_notifications.url_nam = 'run'
run_notifications.verbose_name = 'Run'
run_notifications.description = 'Execute this notifications and send alerts if needed.'


def restore_notifications(modeladmin, request, queryset):
    for num, notification in enumerate(queryset):
        notification.subject = notification.instance.default_subject
        notification.message = notification.instance.default_message
        notification.save()
    msg = '%i notifications have been restored.' % (num+1)
    modeladmin.message_user(request, msg)
restore_notifications.short_description = 'Restore subject and message'
restore_notifications.url_name = 'restore'
restore_notifications.verbose_name = 'Restore default message'
restore_notifications.description = ('Override current subject and message for '
    'the one provided by default.')


sync_notifications = sync_plugins_action('notifications')


@transaction.atomic
def enable_selected(modeladmin, request, queryset):
    queryset.update(is_active=True)
    msg = 'Selected %i notifications have been enabled.' % queryset.count()
    modeladmin.message_user(request, msg)
enable_selected.description = "Enable selected notifications."
enable_selected.short_description = "Enable selected notifications"


@transaction.atomic
def disable_selected(modeladmin, request, queryset):
    queryset.update(is_active=False)
    msg = 'Selected %i notifications have been disabled.' % queryset.count()
    modeladmin.message_user(request, msg)
disable_selected.description = "Disable selected notifications."
disable_selected.short_description = "Disable selected notifications"

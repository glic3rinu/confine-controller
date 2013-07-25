from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin
from django.shortcuts import redirect

from controller.admin import ChangeViewActions
from controller.admin.utils import action_to_view, wrap_admin_view
from controller.utils.plugins import sync_plugins_action

from notifications.actions import (enable_selected, disable_selected, run_notifications,
    upgrade_notifications)
from notifications.models import Notification, Delivered


class DeliveredInline(admin.TabularInline):
    fields = ('content_object', 'date', 'is_valid')
    readonly_fields = ('content_object', 'date', 'is_valid')
    model = Delivered
    
    def has_add_permission(self, *args, **kwargs):
        return False


class NotificationAdmin(ChangeViewActions):
    list_display = ('label', 'module', 'is_active', 'description')
    list_editable = ('is_active',)
    fields = ('description', 'label', 'module', 'subject', 'message', 'is_active')
    readonly_fields = ('label', 'module', 'description')
    list_filter = ('is_active',)
    inlines = [DeliveredInline]
    actions = [enable_selected, disable_selected, run_notifications, upgrade_notifications]
    change_view_actions = [run_notifications, upgrade_notifications]
    
    def get_urls(self):
        urls = super(NotificationAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        extra_urls = patterns("",
            url("^sync-plugins/$",
                wrap_admin_view(self, NotificationAdmin(Notification, admin_site).sync_plugins_view),
                name='notifications_notification_sync_plugins'),
        )
        return extra_urls + urls
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make some char input widgets larger """
        if db_field.name == 'subject':
            kwargs['widget'] = forms.TextInput(attrs={'size':'118'})
        return super(NotificationAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def sync_plugins_view(self, request):
        sync_plugins_action('notifications')(self, request, None)
        return redirect('admin:notifications_notification_changelist')


admin.site.register(Notification, NotificationAdmin)

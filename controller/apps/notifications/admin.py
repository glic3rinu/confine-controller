from django import forms
from django.contrib import admin

from .actions import (enable_selected, disable_selected, run_notifications,
    upgrade_notifications)
from .models import Notification, Delivered


class DeliveredInline(admin.TabularInline):
    fields = ('content_object', 'date', 'is_valid')
    readonly_fields = ('content_object', 'date', 'is_valid')
    model = Delivered
    
    def has_add_permission(self, *args, **kwargs):
        return False


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('label', 'module', 'is_active', 'description')
    fields = ('description', 'label', 'module', 'subject', 'message', 'is_active')
    readonly_fields = ('label', 'module', 'description')
    list_filter = ('is_active',)
    inlines = [DeliveredInline]
    actions = [enable_selected, disable_selected, run_notifications, upgrade_notifications]
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make some char input widgets larger """
        if db_field.name == 'subject':
            kwargs['widget'] = forms.TextInput(attrs={'size':'118'})
        return super(NotificationAdmin, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(Notification, NotificationAdmin)

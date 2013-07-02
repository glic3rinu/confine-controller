from django.contrib import admin

from .models import Notification, Delivered


class DeliveredInline(admin.TabularInline):
    fields = ('content_object', 'date', 'is_valid')
    readonly_fields = ('content_object', 'date', 'is_valid')
    model = Delivered
    can_delete = False
    
    def has_add_permission(self, *args, **kwargs):
        return False


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('label', 'module', 'is_active', 'description')
    fields = ('description', 'label', 'module', 'message', 'is_active')
    readonly_fields = ('label', 'module', 'description')
    inlines = [DeliveredInline]
    
    def has_add_permission(self, *args, **kwargs):
        return False

    # TODO notify, enable, disable and syncnotifications actions.

admin.site.register(Notification, NotificationAdmin)

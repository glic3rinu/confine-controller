from django.contrib import admin
from ticket_system import models


class MessageInline(admin.TabularInline):
    model = models.Ticket

class TicketAdmin(admin.ModelAdmin):
    inlines = [
        MessageInline
        ]
    class Meta:
        model = models.Ticket


class QueueAdmin(admin.ModelAdmin):
    class Meta:
        model = models.Queue

admin.site.register(models.Ticket, TicketAdmin)
admin.site.register(models.Queue, QueueAdmin)

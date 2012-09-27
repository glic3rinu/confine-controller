from django.contrib import admin
from models import Ticket, Queue, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    max_num = 0


class TicketAdmin(admin.ModelAdmin):
    inlines = [MessageInline]


class QueueAdmin(admin.ModelAdmin):
    inlines = [TicketInline]


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Queue, QueueAdmin)

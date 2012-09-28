from common.admin import admin_link_factory
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
    list_display = ['id', 'subject', admin_link_factory('created_by'), 
        admin_link_factory('owner'), admin_link_factory('queue', app_model='issues_queue'),
        'priority', 'state']
    #TODO: create a list filter for 'owner__username'
    list_filter = ['queue', 'priority', 'state']
    inlines = [MessageInline]


class QueueAdmin(admin.ModelAdmin):
    inlines = [TicketInline]


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Queue, QueueAdmin)

from common.admin import admin_link, colored
from django.contrib import admin
from models import Ticket, Queue, Message


PRIORITY_COLORS = { 'HIGH': 'red',
                    'MEDIUM': 'darkorange',
                    'LOW': 'green',}


STATE_COLORS = { 'NEW': 'grey',
                 'OPEN': 'darkorange',
                 'RESOLVED': 'green',
                 'REJECTED': 'yellow' }

class MessageInline(admin.TabularInline):
    model = Message
    extra = 1


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    max_num = 0


class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', admin_link('created_by'), 
        admin_link('owner'), admin_link('queue', app_model='issues_queue'),
        colored('priority', PRIORITY_COLORS), colored('state', STATE_COLORS), 
        'created_on', 'last_modified_on']
    #TODO: create a list filter for 'owner__username'
    list_filter = ['queue__name', 'priority', 'state']
    date_hierarchy = 'created_on'
    search_fields = ['id', 'subject', 'created_by__username', 'created_by__email', 
        'queue', 'owner__username']
    inlines = [MessageInline]
    readonly_fields = ('created_by',)
    fieldsets = (
        (None, {
            'fields': ('created_by', 'subject', ('queue', 'owner'), ('priority', 'state'))
        }),
        ('CC', {
            'classes': ('collapse',),
            'fields': ('cc',)
        }),)
    add_fieldsets = (
        (None, {
            'fields': ('subject', ('queue', 'owner'), ('priority', 'state'))
        }),
        ('CC', {
            'classes': ('collapse',),
            'fields': ('cc',)
        }),)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(TicketAdmin, self).get_fieldsets(request, obj)


class QueueAdmin(admin.ModelAdmin):
    inlines = [TicketInline]


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Queue, QueueAdmin)

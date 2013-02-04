from __future__ import absolute_import

from django.contrib import admin
from django.db import models

from common.admin import admin_link, colored, ChangeViewActionsModelAdmin
from issues.actions import (reject_tickets, resolve_tickets, take_tickets, 
    mark_as_unread)

from .forms import MessageInlineForm, TicketInlineForm
from .models import Ticket, Queue, Message


PRIORITY_COLORS = { 
    Ticket.HIGH: 'red',
    Ticket.MEDIUM: 'darkorange',
    Ticket.LOW: 'green',}

STATE_COLORS = { 
    Ticket.NEW: 'grey',
    Ticket.OPEN: 'darkorange',
    Ticket.RESOLVED: 'green',
    Ticket.REJECTED: 'yellow' }


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    form = MessageInlineForm
    
    def get_formset(self, request, *args, **kwargs):
        """ hook request.user on the inline form """
        self.form.user = request.user
        return super(MessageInline, self).get_formset(request, *args, **kwargs)


class TicketInline(admin.TabularInline):
    model = Ticket
    form = TicketInlineForm
    extra = 0
    max_num = 0


class TicketAdmin(ChangeViewActionsModelAdmin):
    # TODO Bold (id, subject) when tickets are unread for request.user
    # TODO Create a list filter for 'owner__username'
    list_display = ['id', 'subject', admin_link('created_by'), admin_link('owner'),
                    admin_link('queue'), colored('priority', PRIORITY_COLORS),
                    colored('state', STATE_COLORS), 'num_messages', 'created_on',
                    'last_modified_on']
    list_display_links = ('id', 'subject')
    list_filter = ['queue__name', 'priority', 'state']
    date_hierarchy = 'created_on'
    search_fields = ['id', 'subject', 'created_by__username', 'created_by__email',
                     'queue', 'owner__username']
    inlines = [MessageInline]
    actions = [reject_tickets, resolve_tickets, take_tickets, mark_as_unread]
    change_view_actions = [('reject', reject_tickets, '', ''),
                           ('resolve', resolve_tickets, '', ''),
                           ('take', take_tickets, '', ''),]
    readonly_fields = ('created_by',)
    fieldsets = (
        (None, {
            'fields': ('created_by', 'subject', ('owner', 'queue'), ('priority',
                       'state'))
        }),
        ('CC', {
            'classes': ('collapse',),
            'fields': ('cc',)
        }),)
    add_fieldsets = (
        (None, {
            'fields': ('subject', ('owner', 'queue'), ('priority', 'state'))
        }),
        ('CC', {
            'classes': ('collapse',),
            'fields': ('cc',)
        }),)
    
    def num_messages(self, ticket):
        return ticket.messages.count()
    num_messages.short_description = 'Messages'
    num_messages.admin_order_field = 'messages__count'
    
    def queryset(self, request):
        qs = super(TicketAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('messages'))
        return qs
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(TicketAdmin, self).get_fieldsets(request, obj)
    
    def save_model(self, request, obj, *args, **kwargs):
        obj.created_by = request.user
        super(TicketAdmin, self).save_model(request, obj, *args, **kwargs)
    
    def get_form(self, request, *args, **kwargs):
        """ Ugly trick for providing default ticket queue """
        try: query_string = 'queue=%s' % Queue.objects.get_default().id
        except Queue.DoesNotExist: pass
        else:  request.META['QUERY_STRING'] = query_string
        return super(TicketAdmin, self).get_form(request, *args, **kwargs)


class QueueAdmin(admin.ModelAdmin):
    list_display = ['name', 'default', 'num_tickets']
    list_editable = ['default']
    inlines = [TicketInline]
    
    def num_tickets(self, queue):
        return queue.tickets.count()
    num_tickets.short_description = 'Tickets'
    num_tickets.admin_order_field = 'tickets__count'
    
    def queryset(self, request):
        qs = super(QueueAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('tickets'))
        return qs


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Queue, QueueAdmin)

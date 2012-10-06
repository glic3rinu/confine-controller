from common.admin import admin_link, colored
from django.contrib import admin
from issues.actions import reject_tickets, resolve_tickets, open_tickets, take_tickets, mark_as_unread
from issues.forms import MessageInlineForm
from issues.models import Ticket, Queue, Message


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
    form = MessageInlineForm

    def get_formset(self, request, *args, **kwargs):
        """ hook request.user on the inline form """
        self.form.user = request.user
        return super(MessageInline, self).get_formset(request, *args, **kwargs)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    max_num = 0


class TicketAdmin(admin.ModelAdmin):
    #TODO: Bold (id, subject) when tickets are unread for request.user
    #TODO: create a list filter for 'owner__username'
    list_display = ['id', 'subject', admin_link('created_by'), 
        admin_link('owner'), admin_link('queue'),
        colored('priority', PRIORITY_COLORS), colored('state', STATE_COLORS), 
        'created_on', 'last_modified_on']
    list_display_links = ('id', 'subject')
    list_filter = ['queue__name', 'priority', 'state']
    date_hierarchy = 'created_on'
    search_fields = ['id', 'subject', 'created_by__username', 'created_by__email', 
        'queue', 'owner__username']
    inlines = [MessageInline]
    actions = [reject_tickets, resolve_tickets, open_tickets, take_tickets, mark_as_unread]
    readonly_fields = ('created_by',)
    fieldsets = (
        (None, {
            'fields': ('created_by', 'subject', ('owner', 'queue'), ('priority', 'state'))
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
    list_display = ('name', 'default')
    list_editable = ('default', )
    inlines = [TicketInline]


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Queue, QueueAdmin)

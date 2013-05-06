from __future__ import absolute_import

from django.contrib import admin
from django.contrib.auth import get_user_model 
from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe

from controller.admin import ChangeViewActions
from controller.admin.utils import admin_link, colored
from controller.forms import RequiredInlineFormSet
from issues.actions import (reject_tickets, resolve_tickets, take_tickets,
    open_tickets, mark_as_unread)
from permissions.admin import PermissionTabularInline, PermissionModelAdmin

from .filters import MyTicketsListFilter
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


class MessageInline(PermissionTabularInline):
    model = Message
    extra = 1
    form = MessageInlineForm
    formset = RequiredInlineFormSet
    can_delete = False
    
    def get_formset(self, request, obj=None, **kwargs):
        """ hook request.user on the inline form """
        self.form.user = request.user
        return super(MessageInline, self).get_formset(request, obj, **kwargs)


class TicketInline(PermissionTabularInline):
    model = Ticket
    form = TicketInlineForm
    extra = 0
    max_num = 0


class TicketAdmin(ChangeViewActions, PermissionModelAdmin):
    # TODO Bold (id, subject) when tickets are unread for request.user
    list_display = ['id', 'subject', admin_link('created_by'), admin_link('owner'),
                    admin_link('queue'), colored('priority', PRIORITY_COLORS),
                    colored('state', STATE_COLORS), 'last_modified_on']
    list_display_links = ('id', 'subject')
    list_filter = [MyTicketsListFilter, 'queue__name', 'priority', 'state', 'visibility']
    date_hierarchy = 'created_on'
    search_fields = ['id', 'subject', 'created_by__username', 'created_by__email',
                     'queue', 'owner__username']
    inlines = [MessageInline]
    actions = [open_tickets, reject_tickets, resolve_tickets, take_tickets]#, mark_as_unread]
    change_view_actions = [open_tickets, reject_tickets, resolve_tickets, take_tickets]
    change_form_template = "admin/issues/ticket/change_form.html"
    readonly_fields = ('created_by', 'state', 'colored_state')
    fieldsets = (
        (None, {
            'fields': ('created_by', 'subject', ('owner', 'queue'), ('priority',
                       'visibility', 'colored_state'))
        }),
        ('CC', {
            'classes': ('collapse',),
            'fields': ('cc',)
        }),)
    add_fieldsets = (
        (None, {
            'fields': ('subject', ('owner', 'queue'), ('priority', 'visibility', 
                       'colored_state'))
        }),
        ('CC', {
            'classes': ('collapse',),
            'fields': ('cc',)
        }),)
    
    def colored_state(self, instance):
        """ State colored for change_form """
        return  mark_safe(colored(instance.state, STATE_COLORS)(instance))
    colored_state.short_description = "State"
    colored_state.allow_tags = True
    
    def queryset(self, request):
        qs = super(TicketAdmin, self).queryset(request)
        if not request.user.is_superuser:
            qset = Q(visibility=Ticket.PUBLIC)
            qset = Q(qset | Q(visibility=Ticket.PRIVATE, created_by=request.user))
            qset = Q(qset | Q(visibility=Ticket.INTERNAL, created_by__groups__users=request.user))
            qs = qs.filter(qset).distinct()
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
        try:
            query_string = 'queue=%s' % Queue.objects.get_default().id
        except Queue.DoesNotExist:
            pass
        else:
            request.META['QUERY_STRING'] = query_string
        return super(TicketAdmin, self).get_form(request, *args, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """ Only superusers can change owner field """
        readonly_fields = super(TicketAdmin, self).get_readonly_fields(request, obj=obj)
        if not request.user.is_superuser:
            readonly_fields += ('owner',)
        return readonly_fields
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Filter change view actions based on ticket state """
        act = self.change_view_actions
        instance = Ticket.objects.get(pk=object_id)
        if instance.state in ['NEW', 'OPEN']:
            actions_filter = [a.url_name for a in act if a.url_name != 'open']
        else:
            actions_filter = [a.url_name for a in act if a.url_name == 'open']

        extra_context = extra_context or {}
        extra_context['actions_filter'] = actions_filter
        return super(TicketAdmin, self).change_view(request, object_id,
            form_url, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        """ Default filter as 'my_tickets=True' """
        if not request.GET.has_key('my_tickets'):
            q = request.GET.copy()
            q['my_tickets'] = 'True' if not request.user.is_superuser else 'False'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(TicketAdmin,self).changelist_view(request, extra_context=extra_context)

    def get_actions(self, request):
        """ Only superusers can manage tickets """
        actions = super(TicketAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            actions = []
        return actions

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """ 
        Normal users can only select public or private visibility.
        Internal visibility is reserved for operators staff
        """
        if db_field.name == "visibility" and not request.user.is_superuser:
            kwargs['choices'] = (
                (Ticket.PUBLIC,  "Public"),
                (Ticket.PRIVATE, "Private"),
            )
        return super(TicketAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ Filter owner choices to be only superusers """
        if db_field.name == 'owner':
            User = get_user_model()
            kwargs['queryset'] = User.objects.exclude(is_superuser=False)
        return super(TicketAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class QueueAdmin(PermissionModelAdmin):
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

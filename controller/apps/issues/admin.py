from __future__ import absolute_import

from django.conf.urls import patterns
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from markdown import markdown

from controller.admin import ChangeViewActions, ChangeListDefaultFilter
from controller.admin.utils import admin_link, get_admin_link, colored, wrap_admin_view
from permissions.admin import PermissionTabularInline, PermissionModelAdmin

from issues.actions import (reject_tickets, resolve_tickets, take_tickets,
    open_tickets, mark_as_unread, mark_as_read, set_default_queue)
from issues.filters import MyTicketsListFilter, TicketStateListFilter
from issues.forms import MessageInlineForm, TicketForm
from issues.helpers import format_date, get_ticket_changes, html_formated_changes
from issues.models import Ticket, Queue, Message


# TODO remove add another messages
# TODO format_date on controller.utils 
# TODO refactor remaining files

PRIORITY_COLORS = { 
    Ticket.HIGH: 'red',
    Ticket.MEDIUM: 'darkorange',
    Ticket.LOW: 'green',}

STATE_COLORS = { 
    Ticket.NEW: 'grey',
    Ticket.IN_PROGRESS: 'darkorange',
    Ticket.FEEDBACK: 'purple',
    Ticket.RESOLVED: 'green',
    Ticket.REJECTED: 'firebrick',
    Ticket.CLOSED: 'black',}


class MessageReadOnlyInline(admin.TabularInline):
    model = Message
    extra = 0
    can_delete = False
    fields = ['content_html', 'author_link', 'created_on_html']
    readonly_fields = ('content_html', 'author_link', 'created_on_html')
    
    def author_link(self, obj):
        return admin_link('author')(obj)
    author_link.short_description = "Author"
    
    def content_html(self, obj):
        return markdown(obj.content)
    content_html.allow_tags = True
    content_html.short_description = "Content"
    
    def created_on_html(self, obj):
        return format_date(obj.created_on)
    created_on_html.allow_tags = True
    created_on_html.short_description = "Created on"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class MessageInline(PermissionTabularInline):
    model = Message
    extra = 1
    max_num = 1
    form = MessageInlineForm
    can_delete = False
    fields = ['content']
    
    def get_formset(self, request, obj=None, **kwargs):
        """ hook request.user on the inline form """
        self.form.user = request.user
        return super(MessageInline, self).get_formset(request, obj, **kwargs)
    
    def queryset(self, request):
        """ Don't show any message """
        qs = super(MessageInline, self).queryset(request)
        return qs.none()


class TicketInline(PermissionTabularInline):
    model = Ticket
    extra = 0
    max_num = 0
    fields = ['ticket_id', 'subject', 'created_by_link', 'owner_link', 'colored_state', 'colored_priority', 'created', 'last_modified']
    readonly_fields =  ['ticket_id', 'subject', 'created_by_link', 'owner_link', 'colored_state', 'colored_priority', 'created', 'last_modified']

    def ticket_id(self, instance):
        return mark_safe('<b>%s</b>' % get_admin_link(instance))
    ticket_id.short_description = 'ID'
    
    def created_by_link(self, instance):
        return get_admin_link(instance.created_by)
    created_by_link.short_description = 'Created by'
    
    def owner_link(self, instance):
        return get_admin_link(instance.owner)
    owner_link.short_description = 'Owner'
    
    def colored_state(self, instance):
        return colored('state', STATE_COLORS, bold=False)(instance)
    colored_state.short_description = 'State'
    
    def colored_priority(self, instance):
        return colored('priority', PRIORITY_COLORS, bold=False)(instance)
    colored_priority.short_description = 'Priority'
    
    def created(self, instance):
        return instance.created_on.strftime("%Y-%m-%d %H:%M:%S")
    created.short_description = 'Created'
    
    def last_modified(self, instance):
        return instance.last_modified_on.strftime("%Y-%m-%d %H:%M:%S")
    last_modified.short_description = 'Last modified'


class TicketAdmin(ChangeViewActions, ChangeListDefaultFilter, PermissionModelAdmin):
    class Media:
        js = ('issues/js/admin-ticket.js',)
        css = {
             'all': ('issues/css/admin-ticket.css',)
        }
    form = TicketForm
    list_display = ['unbold_id', 'bold_subject', admin_link('created_by'),
        admin_link('owner'), admin_link('queue'), colored('priority', PRIORITY_COLORS),
        colored('state', STATE_COLORS), 'last_modified_on']
    list_display_links = ('unbold_id', 'bold_subject')
    list_filter = [MyTicketsListFilter, 'queue__name', 'priority', TicketStateListFilter,
       'visibility']
    default_changelist_filters = (
        ('my_tickets', lambda r: 'True' if not r.user.is_superuser else 'False'),
        ('state', 'OPEN'))
    date_hierarchy = 'created_on'
    search_fields = ['id', 'subject', 'created_by__username', 'created_by__email',
        'queue', 'owner__username']
    actions = [mark_as_unread, mark_as_read, 'delete_selected', open_tickets,
               reject_tickets, resolve_tickets, take_tickets]
    sudo_actions = ['delete_selected', open_tickets, reject_tickets, resolve_tickets,
                    take_tickets]
    change_view_actions = [open_tickets, reject_tickets, resolve_tickets, take_tickets]
    change_form_template = "admin/issues/ticket/change_form.html"
    readonly_fields = ('abstract', 'colored_state', 'created_by', 'state', 'group')
    fieldsets = (
        (None, {
            'classes': ('relative',),
            'fields': (('abstract', 'subject'), 
                      ('queue', 'state', 'priority', 'visibility', 'group', 'owner'), 'description')
        }),
        ('CC', {
            'classes': ('collapse',),
            'fields': ('cc',)
        }),)
    add_fieldsets = (
        (None, {
            'classes': ('relative',),
            'fields': (('subject', 'colored_state'),
                      ('queue', 'priority', 'visibility','owner'), 'description')
        }),
        ('CC', {
            'classes': ('collapse',),
            'fields': ('cc',)
        }),)
    
    def abstract(self, ticket):
        """ Provide a ticket abstract: subject, creator and state """
        created_by_url = admin_link('created_by')(ticket)
        created_on = ticket.created_on.strftime("%Y-%m-%d")
        state = self.colored_state(ticket)
        subject = "%s<a id='subject-edit' href='#' title='edit'></a>" % ticket.subject
        return ("<div class='field-box'>"
                "    <span class='h3'>Issue #%s - %s</span><br/>"
                "    <span class='created_by'>created by %s at %s</span>"
                "</div>"
                "<div class='field-box field-state'>%s</div>" %
                    (ticket.id, subject, created_by_url, created_on, state))
    abstract.short_description = ""
    abstract.allow_tags = True
    
    def colored_state(self, ticket):
        """ State colored for change_form """
        return  mark_safe(colored(ticket.state, STATE_COLORS)(ticket))
    colored_state.short_description = "State"
    colored_state.allow_tags = True
    
    def unbold_id(self, ticket):
        """ Unbold id if thicket is readed """
        if ticket.is_read_by(self.user):
            return '<span style="font-weight:normal;">%s</span>' % ticket.pk
        return ticket.pk
    unbold_id.allow_tags = True
    unbold_id.short_description = "ID"
    
    def bold_subject(self, ticket):
        """ Bold subject when tickets are unread for request.user """
        if ticket.is_read_by(self.user):
            return ticket.subject
        return "<strong class='unread'>%s</strong>" % ticket.subject
    bold_subject.allow_tags = True
    bold_subject.short_description = "Subject"
    
    def queryset(self, request):
        """ Filter tickets according to their visibility preference """
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
    
    def get_readonly_fields(self, request, obj=None):
        """ Only superusers can change owner field """
        readonly_fields = super(TicketAdmin, self).get_readonly_fields(request, obj=obj)
        if not request.user.is_superuser:
            readonly_fields += ('owner',)
        return readonly_fields
    
    def add_view(self, request, form_url='', extra_context=None):
        """ Do not sow message inlines """
        self.inlines = []
        return super(TicketAdmin, self).add_view(request, form_url, extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Change view actions based on ticket state """
        ticket = get_object_or_404(Ticket, pk=object_id)
        messages = Message.objects.filter(ticket=object_id).order_by('-created_on')
        last_message = messages[0] if messages else False
        
        # Change view actions based on ticket state
        if not hasattr(self, 'change_view_actions_backup'):
            self.change_view_actions_backup = list(self.change_view_actions)
        actions = self.change_view_actions_backup
        if ticket.state in [Ticket.NEW]:
            self.change_view_actions = [a for a in actions if a.url_name != 'open']
        else:
            self.change_view_actions = [a for a in actions if a.url_name == 'open']
        
        # only include messages inline for change view
        self.inlines = [ MessageReadOnlyInline, MessageInline ]
        
        if request.method == 'POST':
            # Hack: Include the ticket changes on the request.POST
            #       other approaches get really messy
            changes = get_ticket_changes(self, request, ticket)
            if changes:
                content = html_formated_changes(changes)
                content += request.POST[u'messages-2-0-content']
                request.POST[u'messages-2-0-content'] = content
        ticket.mark_as_read_by(request.user)
        return super(TicketAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context)
    
    def changelist_view(self, request, extra_context=None):
        # Hook user for bold_subject
        self.user = request.user
        return super(TicketAdmin,self).changelist_view(request, extra_context=extra_context)
    
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """ Remove INTERNAL visibility choice for unprivileged users """
        if db_field.name == "visibility" and not request.user.is_superuser:
            kwargs['choices'] = [ c for c in db_field.choices if c[0] != Ticket.INTERNAL ]
        return super(TicketAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ Filter owner choices to be only superusers """
        if db_field.name == 'owner':
            User = get_user_model()
            kwargs['queryset'] = User.objects.exclude(is_superuser=False)
        return super(TicketAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, *args, **kwargs):
        """ Define creator for new tickets """
        if not obj.pk:
            obj.created_by = request.user
        super(TicketAdmin, self).save_model(request, obj, *args, **kwargs)
        obj.mark_as_read_by(request.user)
    
    def get_urls(self):
        """ add markdown preview url """
        urls = super(TicketAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^preview/$', wrap_admin_view(self, self.message_preview_view))
        )
        return my_urls + urls
    
    def message_preview_view(self, request):
        """ markdown preview render via ajax """
        from markdown import markdown
        data = request.POST.get("data")
        markdown = markdown(strip_tags(data))
        # bugfix preview break lines differs from final result
        markdown = '<br />'.join(markdown.split('\n'))
        return HttpResponse(markdown)


class QueueAdmin(PermissionModelAdmin):
    class Media:
        css = { 'all': ('issues/css/admin-queue.css',) }
    
    actions = [set_default_queue]
    list_display = ['name', 'default', 'num_tickets']
    inlines = [TicketInline]
    ordering = ['name']
    
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

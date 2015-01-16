from __future__ import absolute_import

from django import forms
from django.conf.urls import patterns
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from markdown import markdown

from controller.admin import ChangeViewActions, ChangeListDefaultFilter
from controller.admin.utils import (get_admin_link, colored, wrap_admin_view, display_timesince)
from permissions.admin import PermissionTabularInline, PermissionModelAdmin

from .actions import (reject_tickets, resolve_tickets, take_tickets,close_tickets,
    mark_as_unread, mark_as_read, set_default_queue)
from .filters import MyTicketsListFilter, TicketStateListFilter
from .forms import MessageInlineForm, TicketForm
from .helpers import (display_author, filter_actions, get_ticket_changes,
    markdown_formated_changes)
from .models import Ticket, Queue, Message


PRIORITY_COLORS = { 
    Ticket.HIGH: 'red',
    Ticket.MEDIUM: 'darkorange',
    Ticket.LOW: 'green',
}


STATE_COLORS = { 
    Ticket.NEW: 'grey',
    Ticket.IN_PROGRESS: 'darkorange',
    Ticket.FEEDBACK: 'purple',
    Ticket.RESOLVED: 'green',
    Ticket.REJECTED: 'firebrick',
    Ticket.CLOSED: 'grey',
}


class MessageReadOnlyInline(admin.TabularInline):
    model = Message
    extra = 0
    can_delete = False
    fields = ['content_html']
    readonly_fields = ['content_html']
    
    def content_html(self, obj):
        time = display_timesince(obj.created_on)
        author_link = display_author(obj, 'author')
        summary = 'Updated by %s about %s' % (author_link, time)
        header = '<span class="header">%s</span><hr />' % summary
        content = markdown(obj.content)
        content = content.replace('>\n', '>')
        return header + content
    content_html.allow_tags = True
    content_html.short_description = "Content"
    
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
    
    def get_queryset(self, request):
        """ Don't show any message """
        qs = super(MessageInline, self).get_queryset(request)
        return qs.none()


class TicketInline(PermissionTabularInline):
    fields = [
        'ticket_id', 'subject', 'created_by_link', 'owner_link', 'colored_state',
        'colored_priority', 'created', 'last_modified'
    ]
    readonly_fields =  [
        'ticket_id', 'subject', 'created_by_link', 'owner_link', 'colored_state',
        'colored_priority', 'created', 'last_modified'
    ]
    model = Ticket
    extra = 0
    max_num = 0
    
    def ticket_id(self, instance):
        return mark_safe('<b>%s</b>' % get_admin_link(instance))
    ticket_id.short_description = '#'
    
    def created_by_link(self, instance):
        return display_author(instance, 'created_by')
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
        return display_timesince(instance.created_on)
    
    def last_modified(self, instance):
        return display_timesince(instance.last_modified_on)


class TicketAdmin(ChangeViewActions, ChangeListDefaultFilter, PermissionModelAdmin):
    list_display = [
        'unbold_id', 'bold_subject', 'display_created_by', 'display_group', 'display_owner',
        'display_queue', 'display_priority', 'display_state', 'is_public', 'last_modified'
    ]
    list_display_links = ('unbold_id', 'bold_subject')
    list_filter = [
        MyTicketsListFilter, 'queue__name', 'priority', TicketStateListFilter,
       'visibility'
    ]
    default_changelist_filters = (
        ('my_tickets', lambda r: 'True' if not r.user.is_superuser else 'False'),
        ('state', 'OPEN')
    )
    date_hierarchy = 'created_on'
    search_fields = [
        'id', 'subject', 'created_by__username', 'created_by__email', 'queue__name',
        'owner__username'
    ]
    actions = [
        mark_as_unread, mark_as_read, 'delete_selected', reject_tickets,
        resolve_tickets, close_tickets, take_tickets
    ]
    sudo_actions = ['delete_selected']
    change_view_actions = [
        resolve_tickets, close_tickets, reject_tickets, take_tickets
    ]
    change_form_template = "admin/issues/ticket/change_form.html"
    form = TicketForm
    readonly_fields = (
        'display_summary', 'display_queue', 'display_group', 'display_owner',
        'display_state', 'display_priority', 'display_visibility'
    )
    readonly_fieldsets = (
        (None, {
            'fields': ('display_summary', 
                       ('display_queue', 'display_state', 'display_group',
                        'display_visibility', 'display_priority', 'display_owner'),
                       'display_description')
        }),
    )
    fieldsets = readonly_fieldsets + (
        ('Update', {
            'classes': ('collapse',),
            'fields': ('subject',
                       ('queue', 'state', 'group', 'visibility', 'priority', 'owner'),
                       'description')
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('subject',
                      ('queue', 'state', 'group', 'visibility', 'priority', 'owner'),
                      'description')
        }),
    )
    
    class Media:
        css = {
            'all': ('issues/css/ticket-admin.css',)
        }
        js = (
            'issues/js/ticket-admin.js',
        )
    
    def display_summary(self, ticket):
        author_link = display_author(ticket, 'created_by')
        created = display_timesince(ticket.created_on)
        messages = ticket.messages.order_by('-created_on')
        updated = ''
        if messages:
            updated_on = display_timesince(messages[0].created_on)
            updated_by = get_admin_link(messages[0].author)
            updated = '. Updated by %s about %s' % (updated_by, updated_on)
        msg = '<h4>Added by %s about %s%s</h4>' % (author_link, created, updated)
        return mark_safe(msg)
    display_summary.short_description = 'Summary'
    
    def display_created_by(self, ticket):
        return mark_safe(display_author(ticket, 'created_by'))
    display_created_by.short_description = 'Author'
    
    def display_queue(self, ticket):
        return get_admin_link(ticket.queue) or '-'
    display_queue.short_description = 'queue'
    display_queue.admin_order_field = 'queue'
    
    def display_priority(self, ticket):
        """ State colored for change_form """
        return colored('priority', PRIORITY_COLORS, bold=False, verbose=True)(ticket)
    display_priority.short_description = 'Priority'
    display_priority.admin_order_field = 'priority'
    
    def display_state(self, ticket):
        """ State colored for change_form """
        return colored('state', STATE_COLORS, bold=False, verbose=True)(ticket)
    display_state.short_description = 'State'
    display_state.admin_order_field = 'state'
    
    def display_visibility(self, ticket):
        return ticket.get_visibility_display()
    display_visibility.short_description = 'Visibility'
    display_visibility.admin_order_field = 'visibility'
    
    def display_group(self, ticket):
        return get_admin_link(ticket.group) or '-'
    display_group.short_description = 'Group'
    display_group.admin_order_field = 'group'
    
    def is_public(self, ticket):
        return ticket.visibility == Ticket.PUBLIC
    is_public.short_description = 'Public'
    is_public.admin_order_field = 'visibility'
    is_public.boolean = True
    
    def display_owner(self, ticket):
        return get_admin_link(ticket.owner) or '-'
    display_owner.short_description = 'Assigned to'
    display_owner.admin_order_field = 'owner'
    
    def unbold_id(self, ticket):
        """ Unbold id if ticket is read """
        if ticket.is_read_by(self.user):
            return '<span style="font-weight:normal;font-size:11px;">%s</span>' % ticket.pk
        return ticket.pk
    unbold_id.allow_tags = True
    unbold_id.short_description = "#"
    unbold_id.admin_order_field = 'id'
    
    def bold_subject(self, ticket):
        """ Bold subject when tickets are unread for request.user """
        if ticket.is_read_by(self.user):
            return ticket.subject
        return "<strong class='unread'>%s</strong>" % ticket.subject
    bold_subject.allow_tags = True
    bold_subject.short_description = 'Subject'
    bold_subject.admin_order_field = 'subject'
    
    def last_modified(self, instance):
        return display_timesince(instance.last_modified_on)
    last_modified.admin_order_field = 'last_modified_on'
    
    def get_queryset(self, request):
        """ Filter tickets according to their visibility preference """
        related = ('created_by', 'group', 'queue')
        qs = super(TicketAdmin, self).get_queryset(request).select_related(*related)
        return qs.visible_by(request.user)
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        elif not self.has_change_permission(request, obj=obj, view=False):
            return self.readonly_fieldsets
        return super(TicketAdmin, self).get_fieldsets(request, obj)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'subject':
            kwargs['widget'] = forms.TextInput(attrs={'size':'120'})
        return super(TicketAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
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
    
    def add_view(self, request, form_url='', extra_context=None):
        """ Do not sow message inlines """
        self.inlines = []
        return super(TicketAdmin, self).add_view(request, form_url, extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Change view actions based on ticket state """
        # Check object_id is a valid pk (simplification of ModelAdmin.get_object)
        try:
            int(object_id)
        except ValueError:
            object_id = None
        ticket = get_object_or_404(Ticket, pk=object_id)
        # Change view actions based on ticket state
        self.change_view_actions = filter_actions(self, ticket, request)
        # only include messages inline for change view
        self.inlines = [ MessageReadOnlyInline, MessageInline ]
        if request.method == 'POST':
            # Hack: Include the ticket changes on the request.POST
            #       other approaches get really messy
            changes = get_ticket_changes(self, request, ticket)
            if changes:
                content = markdown_formated_changes(changes)
                content += request.POST[u'messages-2-0-content']
                request.POST[u'messages-2-0-content'] = content
        ticket.mark_as_read_by(request.user)
        context = {
            'title': "Issue #%i - %s" % (ticket.id, ticket.subject),
            'short_title': "Issue #%i" % ticket.id
        }
        context.update(extra_context or {})
        return super(TicketAdmin, self).change_view(
            request, object_id, form_url, extra_context=context)
    
    def changelist_view(self, request, extra_context=None):
        # Hook user for bold_subject
        self.user = request.user
        return super(TicketAdmin,self).changelist_view(request, extra_context=extra_context)
    
    def message_preview_view(self, request):
        """ markdown preview render via ajax """
        data = request.POST.get("data")
        data_formated = markdown(strip_tags(data))
        return HttpResponse(data_formated)


class QueueAdmin(PermissionModelAdmin):
    list_display = [
        'name', 'default', 'notify_group_admins', 'notify_node_admins',
        'notify_slice_admins', 'num_tickets'
    ]
    list_editable = ('notify_group_admins', 'notify_node_admins', 'notify_slice_admins')
    actions = [set_default_queue]
    inlines = [TicketInline]
    ordering = ['name']
    
    class Media:
        css = {
            'all': ('controller/css/hide-inline-id.css',)}
    
    def num_tickets(self, queue):
        num = queue.tickets.count()
        url = reverse('admin:issues_ticket_changelist')
        url += '?my_tickets=False&queue=%i' % queue.pk
        return mark_safe('<a href="%s">%d</a>' % (url, num))
    num_tickets.short_description = 'Tickets'
    num_tickets.admin_order_field = 'tickets__count'
    
    def get_queryset(self, request):
        qs = super(QueueAdmin, self).get_queryset(request)
        qs = qs.annotate(models.Count('tickets'))
        return qs


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Queue, QueueAdmin)

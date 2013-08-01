from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.sites.models import RequestSite
from django.db import transaction
from django.template.response import TemplateResponse

from controller.admin.decorators import action_with_confirmation

from issues.helpers import log_as_message, user_has_perm
from issues.models import Queue


@user_has_perm
@transaction.commit_on_success
def resolve_tickets(modeladmin, request, queryset):
    site = RequestSite(request)
    queryset.resolve(site)
    for ticket in queryset:
        modeladmin.log_change(request, ticket, "Marked as Resolved")
        log_as_message(modeladmin, ticket, request.user)
    msg = "%s selected tickets are now resolved" % queryset.count()
    modeladmin.message_user(request, msg)
resolve_tickets.url_name = 'resolve'


@user_has_perm
@action_with_confirmation('reject', template='admin/issues/reject_confirmation.html')
@transaction.commit_on_success
def reject_tickets(modeladmin, request, queryset):
    if queryset.count() != 1:
        messages.warning(request, "Please, one ticket at a time.")
        return None

    obj = queryset.get()
    site = RequestSite(request)
    reason = request.POST.get('reason') or ''

    queryset.reject(site) 
    modeladmin.log_change(request, obj, "Marked as Rejected")
    log_as_message(modeladmin, obj, request.user, reason)

    msg = "%s selected tickets are now rejected" % queryset.count()
    modeladmin.message_user(request, msg)
reject_tickets.url_name = 'reject'


@user_has_perm
def open_tickets(modeladmin, request, queryset):
    site = RequestSite(request)
    queryset.open(site)
    for ticket in queryset:
        modeladmin.log_change(request, ticket, "Marked as Open")
        log_as_message(modeladmin, ticket, request.user)
    msg = "%s selected tickets are now open" % queryset.count()
    modeladmin.message_user(request, msg)
open_tickets.url_name = 'open'


@user_has_perm
@transaction.commit_on_success
def take_tickets(modeladmin, request, queryset):
    queryset.take(owner=request.user)
    for ticket in queryset:
        modeladmin.log_change(request, ticket, "Taken")
    msg = "%s selected tickets are now owned by %s" % (queryset.count(), request.user)
    modeladmin.message_user(request, msg)
take_tickets.url_name = 'take'


@transaction.commit_on_success
def mark_as_unread(modeladmin, request, queryset):
    """ Mark a tickets as unread """
    for ticket in queryset:
        ticket.mark_as_unread_by(request.user)
    msg = "%s selected tickets has been marked as unread" % queryset.count()
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def mark_as_read(modeladmin, request, queryset):
    """ Mark a tickets as unread """
    for ticket in queryset:
        ticket.mark_as_read_by(request.user)
    msg = "%s selected tickets has been marked as read" % queryset.count()
    modeladmin.message_user(request, msg)


## Queue actions
@user_has_perm
@transaction.commit_on_success
def set_default_queue(modeladmin, request, queryset):
    """ Set a queue as default issues queue """
    if queryset.count() != 1:
        messages.warning(request, "Please, select only one queue.")
        return
    Queue.objects.filter(default=True).update(default=False)
    #queryset.update(default=True)
    queue = queryset.get()
    queue.default = True
    queue.save()
    modeladmin.log_change(request, queue, "Choosed as default.")
    messages.info(request, "Choosed '%s' as default queue." % queue)


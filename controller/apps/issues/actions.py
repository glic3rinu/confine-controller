from django.contrib.sites.models import RequestSite
from django.core.exceptions import PermissionDenied
from django.db import transaction

from issues.models import Message

def user_has_perm(func):
    """ 
    Check if the user has the required permission to execute an action    
    Inspired in user_passes_test from django.contrib.auth.decorators

    """
    def has_perm(modeladmin, request, queryset):
        if request.user.is_superuser:
            return func(modeladmin, request, queryset)
        else:
            raise PermissionDenied()
    has_perm.__name__ = func.__name__
    return has_perm

@user_has_perm
@transaction.commit_on_success
def resolve_tickets(modeladmin, request, queryset):
    site = RequestSite(request)
    queryset.resolve(site)
    for obj in queryset:
        modeladmin.log_change(request, obj, "Marked as Resolved")
    msg = "%s selected tickets are now resolved" % queryset.count()
    modeladmin.message_user(request, msg)
resolve_tickets.url_name = 'resolve'


@user_has_perm
@transaction.commit_on_success
def reject_tickets(modeladmin, request, queryset):
    from django.contrib.admin import helpers
    from django.template.response import TemplateResponse
    opts = modeladmin.model._meta
    app_label = opts.app_label
    print "APP_LABEL: %s" % (app_label)

    if queryset.count() != 1:
        messages.warning(request, "Please, one ticket at a time.")
        return
    

    # The user has alreday confirmed the reject
    if request.POST.get('post'):
        #create new message with reject reason (message)
        reason = request.POST.get('reason')
        if reason:
            ticket = queryset.get()
            reason = "REJECT REASON: %s" % reason
            message = Message(ticket=ticket, author=request.user, content=reason)
            message.save()
        site = RequestSite(request)
        queryset.reject(site) 
        for obj in queryset:
            modeladmin.log_change(request, obj, "Marked as Rejected")
        msg = "%s selected tickets are now rejected" % queryset.count()
        modeladmin.message_user(request, msg)
        return

    context = { 
        "title": "Are you sure?",
        "content_message": "Are you sure you want to reject the selected ticket?",
        "action_name": 'Reject',
        "action_value": 'reject_tickets',
        "deletable_objects": queryset,
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }   

    return TemplateResponse(request, 'admin/issues/reject_confirmation.html',
        context, current_app=modeladmin.admin_site.name)
reject_tickets.url_name = 'reject'

@user_has_perm
def open_tickets(modeladmin, request, queryset):
    site = RequestSite(request)
    queryset.open(site)
    for obj in queryset:
        modeladmin.log_change(request, obj, "Marked as Open")
    msg = "%s selected tickets are now open" % queryset.count()
    modeladmin.message_user(request, msg)
open_tickets.url_name = 'open'

@user_has_perm
@transaction.commit_on_success
def take_tickets(modeladmin, request, queryset):
    queryset.take(owner=request.user)
    for obj in queryset:
        modeladmin.log_change(request, obj, "Taken")
    msg = "%s selected tickets are now owned by %s" % (queryset.count(), request.user)
    modeladmin.message_user(request, msg)
take_tickets.url_name = 'take'

@transaction.commit_on_success
def mark_as_unread(modeladmin, request, queryset):
    #TODO Implement mark a ticket as unread
    raise NotImplementedError("Sorry, but `mark_as_unread` operation is not implemented yet.")


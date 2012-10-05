from django.contrib import messages
from django.db import transaction


@transaction.commit_on_success
def resolve_tickets(modeladmin, request, queryset):
    queryset.resolve()
    msg = "%s selected tickets are now resolved" % queryset.count()
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def open_tickets(modeladmin, request, queryset):
    queryset.open()
    msg = "%s selected tickets are now open" % queryset.count()
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def reject_tickets(modeladmin, request, queryset):
    queryset.reject()
    msg = "%s selected tickets are now rejected" % queryset.count()
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def take_tickets(modeladmin, request, queryset):
    queryset.take(owner=request.user)
    msg = "%s selected tickets are now owned by %s" % (queryset.count(), request.user)
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def mark_as_unread(modeladmin, request, queryset):
    #TODO
    pass


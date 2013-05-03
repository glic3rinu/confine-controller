from django.contrib.sites.models import RequestSite
from django.core.exceptions import PermissionDenied
from django.db import transaction

def is_operator_deco(func):
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

@is_operator_deco
@transaction.commit_on_success
def resolve_tickets(modeladmin, request, queryset):
    site = RequestSite(request)
    queryset.resolve(site)
    for obj in queryset:
        modeladmin.log_change(request, obj, "Marked as Resolved")
    msg = "%s selected tickets are now resolved" % queryset.count()
    modeladmin.message_user(request, msg)
resolve_tickets.url_name = 'resolve'


@is_operator_deco
@transaction.commit_on_success
def reject_tickets(modeladmin, request, queryset):
    site = RequestSite(request)
    queryset.reject(site)
    for obj in queryset:
        modeladmin.log_change(request, obj, "Marked as Rejected")
    msg = "%s selected tickets are now rejected" % queryset.count()
    modeladmin.message_user(request, msg)
reject_tickets.url_name = 'reject'


@is_operator_deco
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


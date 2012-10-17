from django.db import transaction


@transaction.commit_on_success
def resolve_tickets(modeladmin, request, queryset):
    queryset.resolve()
    for obj in queryset:
        modeladmin.log_change(request, obj, "Marked as Resolved")
    msg = "%s selected tickets are now resolved" % queryset.count()
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def reject_tickets(modeladmin, request, queryset):
    queryset.reject()
    for obj in queryset:
        modeladmin.log_change(request, obj, "Marked as Rejected")
    msg = "%s selected tickets are now rejected" % queryset.count()
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def take_tickets(modeladmin, request, queryset):
    queryset.take(owner=request.user)
    for obj in queryset:
        modeladmin.log_change(request, obj, "Taked")
    msg = "%s selected tickets are now owned by %s" % (queryset.count(), request.user)
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def mark_as_unread(modeladmin, request, queryset):
    #TODO
    pass


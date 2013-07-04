from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect

from groupregistration.models import GroupRegistration

@transaction.commit_on_success
def approve_group(modeladmin, request, queryset):
    rows_updated = 0
    for group in queryset:
        try:
            greg = GroupRegistration.objects.get(group=group)
        except GroupRegistration.DoesNotExist:
            continue
        greg.approve()
        rows_updated+=1
        
    messages.info(request, "%s group(s) has been approved" % rows_updated)
    return redirect('admin:users_group_changelist')
approve_group.short_description = "Approve selected groups"

@transaction.commit_on_success
def reject_group(modeladmin, request, queryset):
    rows_updated = 0
    for group in queryset:
        try:
            greg = GroupRegistration.objects.get(group=group)
        except GroupRegistration.DoesNotExist:
            messages.info(request, "You cannot reject an approved group (%s)" % group)
            continue
        greg.reject()
        rows_updated+=1

    messages.info(request, "%s group(s) has been rejected" % rows_updated)
    return redirect('admin:users_group_changelist')
reject_group.short_description = "Reject selected groups"

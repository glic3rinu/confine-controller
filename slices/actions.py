from django.contrib import messages
from django.db import router, transaction


@transaction.commit_on_success
def renew_selected_slices(modeladmin, request, queryset):
    for slice in queryset:
        slice.renew()
    msg = "%s selected slices has been renewed" % queryset.count()
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def reset_selected_slices(modeladmin, request, queryset):
    for slice in queryset:
        slice.reset()
    msg = "%s selected slices has been reseted" % queryset.count()
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def reset_selected_slivers(modeladmin, request, queryset):
    for sliver in queryset:
        sliver.reset()
    msg = "%s selected slices has been reseted" % queryset.count()
    modeladmin.message_user(request, msg)

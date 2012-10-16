from django.contrib import messages
from django.db import router, transaction
from slices import settings


@transaction.commit_on_success
def renew_selected_slices(modeladmin, request, queryset):
    for slice in queryset:
        slice.renew()
        modeladmin.log_change(request, slice, "Renewed for %s" % settings.SLICE_EXPIRATION_INTERVAL)
    msg = "%s selected slices has been renewed for %s on" % (queryset.count(), settings.SLICE_EXPIRATION_INTERVAL)
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def reset_selected_slices(modeladmin, request, queryset):
    for slice in queryset:
        slice.reset()
        modeladmin.log_change(request, slice, "Instructed to reset")
    msg = "%s selected slices has been reseted" % queryset.count()
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def reset_selected_slivers(modeladmin, request, queryset):
    for sliver in queryset:
        sliver.reset()
        modeladmin.log_change(request, sliver, "Instructed to reset")
    msg = "%s selected slices has been reseted" % queryset.count()
    modeladmin.message_user(request, msg)

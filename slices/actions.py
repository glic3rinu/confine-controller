from django.contrib import messages
from django.db import router, transaction


@transaction.commit_on_success
def renew_selected_slices(modeladmin, request, queryset):
    message = "Not implemented!"
    messages.warning(request, message)


@transaction.commit_on_success
def reset_selected_slices(modeladmin, request, queryset):
    message = "Not implemented!"
    messages.warning(request, message)


@transaction.commit_on_success
def reset_selected_slivers(modeladmin, request, queryset):
    message = "Not implemented!"
    messages.warning(request, message)

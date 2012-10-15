from django.contrib import messages
from django.db import transaction


@transaction.commit_on_success
def reboot(modeladmin, request, queryset):
    message = "Not implemented!"
    messages.warning(request, message)


@transaction.commit_on_success
def request_cert(modeladmin, request, queryset):
    message = "Not implemented!"
    messages.warning(request, message)



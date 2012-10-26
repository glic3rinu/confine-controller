from django.contrib import messages
from django.db import transaction
from firmware.tasks import generate_firmware


@transaction.commit_on_success
def get_firmware(modeladmin, request, queryset):
    message = "Not implemented!"
    for node in queryset:
        generate_firmware.delay(node)
    messages.warning(request, message)


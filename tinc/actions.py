from django.contrib import messages
from django.db import transaction


@transaction.commit_on_success
def set_islands(modeladmin, request, queryset):
    message = "Not implemented!"
    messages.warning(request, message)

from django.db import transaction


@transaction.commit_on_success
def set_island(modeladmin, request, queryset):
    for obj in queryset:
        obj.tinc.set_island()
    msg = "Islands has been set for %s selected objects" % queryset.count()
    modeladmin.message_user(request, msg)

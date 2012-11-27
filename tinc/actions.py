from django.core.exceptions import PermissionDenied
from django.db import transaction


@transaction.commit_on_success
def set_island(modeladmin, request, queryset):
    counter = 0
    for obj in queryset:
        if obj.tinc:
            if not obj.tinc.has_permission.change(request.user):
                raise PermissionDenied
            counter += 1
            obj.tinc.set_island()
            modeladmin.log_change(request, obj, "Island setted")
    if counter > 0:
        msg = "Islands has been set for %s selected objects" % counter
        modeladmin.message_user(request, msg)

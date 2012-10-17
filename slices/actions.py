from django.contrib import messages
from django.db import router, transaction
from slices import settings
from django.utils.translation import ugettext_lazy, ugettext as _


@transaction.commit_on_success
def renew_selected_slices(modeladmin, request, queryset):
    for slice in queryset:
        slice.renew()
        modeladmin.log_change(request, slice, "Renewed for %s" % settings.SLICE_EXPIRATION_INTERVAL)
    msg = "%s selected slices has been renewed for %s on" % (queryset.count(), settings.SLICE_EXPIRATION_INTERVAL)
    modeladmin.message_user(request, msg)


@transaction.commit_on_success
def reset_selected(modeladmin, request, queryset):
    for obj in queryset:
        obj.reset()
        modeladmin.log_change(request, obj, "Instructed to reset")
    msg = "%s selected has been reseted" % (obj._meta.verbose_name_plural, queryset.count())
    modeladmin.message_user(request, msg)
reset_selected.short_description = ugettext_lazy("Reset selected %(verbose_name_plural)s")

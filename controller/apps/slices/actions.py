from django.contrib.admin import helpers
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy

from controller.admin.utils import get_admin_link, get_modeladmin

from .forms import SliverIfaceBulkForm
from .models import Slice, Sliver, SliverIface
from .settings import SLICES_SLICE_EXP_INTERVAL


@transaction.atomic
def renew_selected_slices(modeladmin, request, queryset):
    # TODO queryset.renew() ?
    not_renewed = 0
    for obj in queryset:
        if not modeladmin.has_change_permission(request, obj=obj):
            raise PermissionDenied
        if obj.renew():
            msg = "Renewed for %s" % SLICES_SLICE_EXP_INTERVAL
            modeladmin.log_change(request, obj, msg)
        else:
            not_renewed += 1
    renewed = queryset.count() - not_renewed
    if renewed > 0:
        msg = ("%s selected slices have been renewed (expiration date extended "
               "by %s days from now)."  % (renewed, SLICES_SLICE_EXP_INTERVAL.days))
        modeladmin.message_user(request, msg)
    if not_renewed > 0:
        msg = ("%s selected slices have NOT been renewed (alreday have maximum "
               "expiration date)." % not_renewed)
        modeladmin.message_user(request, msg, messages.WARNING)
renew_selected_slices.url_name = 'renew'
renew_selected_slices.description = 'Delay the slice expiration date for %s days.' % SLICES_SLICE_EXP_INTERVAL.days


@transaction.atomic
def reset_selected(modeladmin, request, queryset):
    # TODO queryset.reset() ?
    for obj in queryset:
        if not modeladmin.has_change_permission(request, obj=obj):
            raise PermissionDenied
        obj.reset()
        modeladmin.log_change(request, obj, "Instructed to reset")
    verbose_name_plural = force_text(obj._meta.verbose_name_plural)
    msg = "%s selected %s have been instructed to reset." % (queryset.count(), verbose_name_plural)
    modeladmin.message_user(request, msg)
reset_selected.short_description = ugettext_lazy("Reset selected %(verbose_name_plural)s")
reset_selected.url_name = 'reset'
reset_selected.description = ('Stop, redeploy and restart all the slivers in this '
    'slice without changing their configuration.')


@transaction.atomic
def update_selected(modeladmin, request, queryset):
    # TODO queryset.update() ?
    for obj in queryset:
        if not modeladmin.has_change_permission(request, obj=obj):
            raise PermissionDenied
        obj.update()
        modeladmin.log_change(request, obj, "Instructed to update")
    verbose_name_plural = force_text(obj._meta.verbose_name_plural)
    msg = "%s selected %s have been instructed to update." % (queryset.count(), verbose_name_plural)
    modeladmin.message_user(request, msg)
update_selected.short_description = ugettext_lazy("Update selected %(verbose_name_plural)s")
update_selected.url_name = 'update'
update_selected.description = ('Stop and undeploy this sliver, then try to deploy '
    'it again with its latest configuration.')


@transaction.atomic
def create_slivers(modeladmin, request, queryset):
    """ Create slivers in selected nodes """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    slice = get_object_or_404(Slice, pk=modeladmin.slice_id)
    
    if not modeladmin.has_change_permission(request, obj=slice):
        raise PermissionDenied
    
    n = queryset.count()
    if n == 1:
        node = queryset.get()
        return redirect('admin:slices_slice_add_sliver', modeladmin.slice_id, node.pk)
    
    if request.POST.get('post'):
        form = SliverIfaceBulkForm(slice, queryset, request.POST)
        if form.is_valid():
            optional_ifaces = form.cleaned_data
            requested_ifaces = [ field for field, value in optional_ifaces.iteritems() if value ]
            
            for node in queryset:
                sliver = Sliver(slice=slice, node=node)
                if not request.user.has_perm('slices.add_sliver', sliver):
                    raise PermissionDenied
                sliver.save()
                for iface_type in requested_ifaces:
                    iface = Sliver.get_registered_ifaces()[iface_type]
                    SliverIface.objects.create(sliver=sliver, name=iface.DEFAULT_NAME, type=iface_type)
                slice_modeladmin = get_modeladmin(Slice)
                msg = 'Added sliver "%s"' % force_text(sliver)
                slice_modeladmin.log_change(request, slice, msg)
                sliver_modeladmin = get_modeladmin(Sliver)
                # AUTO_CREATE SliverIfaces
                sliver_modeladmin.log_addition(request, sliver)
            
            modeladmin.message_user(request, "Successfully created %d slivers." % n)
            # Return None to display the change list page again.
            return redirect('admin:slices_slice_change', slice.pk)
    
    context = {
        "title": "Are you sure?",
        "slice": slice,
        "deletable_objects": [[ get_admin_link(node) for node in queryset ]],
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'form': SliverIfaceBulkForm(slice, queryset),
    }
    
    return TemplateResponse(request, "admin/slices/slice/create_slivers_confirmation.html",
                            context, current_app=modeladmin.admin_site.name)
create_slivers.short_description = "Create slivers on selected nodes"
create_slivers.description = create_slivers.short_description

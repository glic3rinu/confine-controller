from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import get_model
from django.http import Http404
from django.shortcuts import redirect

from controller.admin.utils import get_modeladmin
from controller.core.exceptions import OperationLocked

from .tasks import get_state


@transaction.commit_on_success
def refresh(modeladmin, request, queryset):
    """ get_state from State queryset synchronously """
    opts = queryset[0].content_object._meta
    module = '%s.%s' % (opts.app_label, opts.object_name)
    ids = queryset.values_list('object_id', flat=True)
    # Execute get_state isolated on a process to avoid gevent polluting the stack
    # and preventing this silly complain "gevent is only usable from a single thread"
    # Don't know yet why ids has to be copied, otherwise task doesn't get monitored
    # Maybe because somehow ids can not be properly serialized ?? WTF
    result = get_state.delay(module, ids=list(ids), lock=False)
    try:
        # Block until finish
        result.get()
    except OperationLocked:
        msg = 'This operation is currently being executed by another process'
        messages.error(request, msg)
    else:
        msg = 'The state of %d %ss has been updated' % (queryset.count(), opts.object_name)
        modeladmin.message_user(request, msg)
refresh.description = "Retrieve the current state of the related object"
refresh.always_display = True


@transaction.commit_on_success
def refresh_state(modeladmin, request, queryset):
    """ gate_state from Node/Sliver queryset synchronously """
    opts = queryset.model._meta
    module = '%s.%s' % (opts.app_label, opts.object_name)
    ids = queryset.values_list('pk', flat=True)
    # Execute get_state isolated on a process to avoid gevent polluting the stack
    # and preventing this silly complain "gevent is only usable from a single thread"
    # Don't know yet why ids has to be copied, otherwise task doesn't get monitored
    # Maybe because somehow ids can not be properly serialized ?? WTF
    try:
        result = get_state.delay(module, ids=list(ids))
        result.get()
    except OperationLocked:
        msg = 'This operation is currently being executed by another process'
        messages.error(request, msg)
    else:
        msg = 'The state of %d %ss has been updated' % (queryset.count(), opts.object_name)
        modeladmin.message_user(request, msg)


def show_state(modeladmin, request, queryset):
    """ links to state information (state change view) """
    try:
        obj = queryset.get()
    except ObjectDoesNotExist:
        raise Http404
    model_name = obj._meta.verbose_name_raw
    state = obj.state
    return redirect('admin:state_state_change', state.pk)
show_state.url_name = 'state'
show_state.description = "Show the current state of this object"
show_state.always_display = True

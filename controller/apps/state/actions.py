from django.contrib import messages
from django.db import transaction
from django.db.models import get_model
from django.shortcuts import redirect

from controller.admin.utils import get_modeladmin
from controller.utils import LockFile

from .tasks import get_state


@transaction.commit_on_success
def refresh(modeladmin, request, queryset):
    """ get_state from NodeState/SliverState queryset synchronously """
    opts = queryset.model._meta
    state_module = '%s.%s' % (opts.app_label, opts.object_name)
    field_name = queryset.model.get_related_field_name()
    ids = queryset.values_list('%s__id' % field_name , flat=True)
    related_model_name = queryset.model.get_related_model()._meta.object_name
    # Execute get_state isolated on a process to avoid gevent polluting the stack
    result = get_state.delay(state_module, ids=ids)
    try:
        result.get()
    except:
    # FIXME except LockFile.OperationLocked():
        msg = 'This operation is currently being executed by another process'
        messages.error(request, msg)
    else:
        msg = 'The state of %d %ss has been updated' % (queryset.count(), related_model_name)
        modeladmin.message_user(request, msg)


@transaction.commit_on_success
def refresh_state(modeladmin, request, queryset):
    """ gate_state from Node/Sliver queryset synchronously """
    opts = queryset.model._meta
    state_module = 'state.%sState' % opts.object_name
    state_model = get_model(*state_module.split('.'))
    ids = queryset.values_list('state__id', flat=True)
    # Execute get_state isolated on a process to avoid gevent polluting the stack
    try:
        result = get_state.delay(state_module, ids=ids)
        result.get()
    except:
    # FIXME except LockFile.OperationLocked():
        msg = 'This operation is currently being executed by another process'
        messages.error(request, msg)
    else:
        msg = 'The state of %d %ss has been updated' % (queryset.count(), opts.object_name)
        modeladmin.message_user(request, msg)


def state_action(modeladmin, request, queryset):
    obj = queryset.get()
    model_name = obj._meta.verbose_name_raw
    return redirect('admin:state_%sstate_change' % model_name, obj.state.pk)
state_action.url_name = 'state'

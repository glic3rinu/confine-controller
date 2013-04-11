from threading import Thread

from django.db import transaction
from django.db.models import get_model

from .tasks import get_state


@transaction.commit_on_success
def refresh(modeladmin, request, queryset):
    """ get_state from NodeState/SliverState queryset synchronously """
    opts = queryset.model._meta
    state_module = '%s.%s' % (opts.app_label, opts.object_name)
    field_name = queryset.model.get_related_field_name()
    ids = queryset.values_list('%s__id' % field_name , flat=True)
    # Execute get_state isolated on a thread because gevent is only usable from a single thread
    thread = Thread(target=get_state, args=(state_module,), kwargs={'ids':ids})
    thread.start()
    thread.join()
    related_model_name = queryset.model.get_related_model()._meta.object_name
    msg = 'The state of %d %ss has been updated' % (queryset.count(), related_model_name)
    modeladmin.message_user(request, msg)


def refresh_state(modeladmin, request, queryset):
    """ gate_state from Node/Sliver queryset synchronously """
    opts = queryset.model._meta
    state_module = 'state.%sState' % opts.object_name
    state_model = get_model(*state_module.split('.'))
    ids = queryset.values_list('state__id', flat=True)
    # Execute get_state isolated on a thread because gevent is only usable from a single thread
    thread = Thread(target=get_state, args=(state_module,), kwargs={'ids':ids})
    thread.start()
    thread.join()
    msg = 'The state of %d %ss has been updated' % (queryset.count(), opts.object_name)
    modeladmin.message_user(request, msg)

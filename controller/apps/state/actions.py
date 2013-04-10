from django.db import transaction
#from django_transaction_signals import defer

from .tasks import get_state


@transaction.commit_on_success
def refresh(modeladmin, request, queryset):
    opts = queryset.model._meta
    model_label = '%s.%s' % (opts.app_label, opts.object_name)
    field_name = queryset.model.get_related_field_name()
    ids = queryset.values_list('%s__id' % field_name , flat=True)
    # make requests synchronously because we want inmediate feedback
    get_state(model_label, ids=ids)

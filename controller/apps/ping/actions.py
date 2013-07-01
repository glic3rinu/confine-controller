from django.db import transaction

@transaction.commit_on_success
def ping(modeladmin, request, queryset):
    """ get_state from NodeState/SliverState queryset synchronously """
    opts = queryset.model._meta
    print request
ping.description = "Retrieve the current state of the related object"



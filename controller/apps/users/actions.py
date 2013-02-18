from django.contrib import messages
from django.contrib.sites.models import RequestSite
from django.db import transaction

from users.models import JoinRequest


@transaction.commit_on_success
def join_request(modeladmin, request, queryset):
    """
    The user can create request to join some groups.
    If there are any error when creating a request, the process continues
    for the other groups.
    """
    for group in queryset:
        user = request.user
        # check if user is alreday in the group
        if group.users.filter(pk=user.id).exists():
            messages.error(request, "You already are member of group (%s)" % group)
            return
        # get_or_create handle all the transaction stuff:transaction.savepoint ...
        jrequest, created = JoinRequest.objects.get_or_create(user=user, group=group)
        if created:
            site = RequestSite(request)
            jrequest.send_creation_email(site)
            modeladmin.message_user(request, "Your join request has been sent (%s)" % group)
        else:
            modeladmin.message_user(request, "You have alreday sent a request to this group (%s)" % group, messages.ERROR)
        return

join_request.short_description = "Request to join the selected groups"


from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.sites.models import RequestSite
from django.db import router, transaction
from django.template.response import TemplateResponse
from django.utils.encoding import force_text

from users.models import JoinRequest


@transaction.commit_on_success
def join_request(modeladmin, request, queryset):
    """
    The user can create request to join some groups.
    If there are any error when creating a request, the process continues
    for the other groups.
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    using = router.db_for_write(modeladmin.model)
    
    # check if user is alreday in the group
    for group in queryset:
        user = request.user
        if group.users.filter(pk=user.id).exists():
            messages.error(request, "You already are member of group (%s)" % group)
            return
    
    # The user has already confirmed the join request.
    if request.POST.get('post'):
        n = queryset.count()
        if n:
            for group in queryset:
                jrequest, created = JoinRequest.objects.get_or_create(user=user, group=group)
                if created:
                    site = RequestSite(request)
                    jrequest.send_creation_email(site)
                    modeladmin.message_user(request, "Your join request has been sent (%s)" % group)
                else:
                    modeladmin.message_user(request, "You have alreday sent a request to this group (%s)" % group, messages.ERROR)
            return None
    
    if len(queryset) == 1:
        objects_name = force_text(opts.verbose_name)
    else:
        objects_name = force_text(opts.verbose_name_plural)
    
    context = {
        "title": "Are you sure?",
        "content_message": "Are you sure you want to send a join request to the following groups?",
        "action_name": 'Join Request',
        "action_value": 'join_request',
        "deletable_objects": queryset,
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return TemplateResponse(request, 'admin/generic_confirmation.html',
        context, current_app=modeladmin.admin_site.name)

join_request.short_description = "Request to join the selected groups"


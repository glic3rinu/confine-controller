from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.sites.models import RequestSite
from django.db import router, transaction
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from controller.utils.options import send_email_template

from users.forms import SendMailForm
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
    user = request.user
    
    # check if user is alreday in the group
    for group in queryset:
        if group.users.filter(pk=user.id).exists():
            messages.error(request, "You already are member of group (%s)" % group)
            return
        if JoinRequest.objects.filter(user=user, group=group).exists():
            messages.error(request, "You alreday have sent a request to this group (%s)" % group)
            return
    
    # The user has already confirmed the join requests
    if request.POST.get('post'):
        n = queryset.count()
        if n:
            for group in queryset:
                jrequest, created = JoinRequest.objects.get_or_create(user=user, group=group)
                if created:
                    site = RequestSite(request)
                    jrequest.send_creation_email(site)
                    modeladmin.message_user(request, "Your join request has been sent (%s)" % group)
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
    return TemplateResponse(request, 'admin/controller/generic_confirmation.html',
        context, current_app=modeladmin.admin_site.name)
join_request.short_description = "Request to join the selected groups"
join_request.url_name = 'join-request'


@transaction.commit_on_success
def enable_account(modeladmin, request, queryset):
    """
    The testbed operators can enable the users
    """
    opts = modeladmin.model._meta
    
    # check if the selected user is alreday enabled
    for user in queryset:
        if user.is_active:
            messages.error(request, "This user is alreday active (%s)" % user)
            continue
        user.is_active = True
        user.save()
        # notify the user its account is enabled
        site = RequestSite(request)
        send_email_template('registration/account_approved.email', {'site': site}, user.email)
        modeladmin.message_user(request, "The user has been enabled (%s)" % user)
enable_account.short_description = "Enable selected users"


def send_email(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = SendMailForm()
    
    # User has provided a SCR
    if request.POST.get('post'):
        form = SendMailForm(request.POST)
        if form.is_valid():
            scr = form.cleaned_data['scr']
            modeladmin.log_change(request, node, "Certificate requested")
            return
    
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    context = {
        "title": "Send mail to users",
        "content_title": '',
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        "form": form,
    }
    
    # Display the confirmation page
    return TemplateResponse(request, 'admin/users/user/send_email.html', context, 
        current_app=modeladmin.admin_site.name)

send_email.url_name = 'send-email'
send_email.verbose_name = 'Send Email'

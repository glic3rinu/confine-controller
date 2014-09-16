from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.sites.models import RequestSite
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mass_mail
from django.db import transaction
from django.template.response import TemplateResponse
from django.utils.encoding import force_text

from controller.admin.decorators import action_with_confirmation

from .forms import SendMailForm, ConfirmSendMailForm
from .models import JoinRequest


@action_with_confirmation('send a join request to')
@transaction.atomic
def join_request(modeladmin, request, queryset):
    """
    The user can create request to join some groups.
    If there are any error when creating a request, the process continues
    for the other groups.
    """
    user = request.user
    
    # check if user is alreday in the group
    for group in queryset:
        if group.users.filter(pk=user.id).exists():
            messages.error(request, "You already are member of group (%s)" % group)
            return None
        if JoinRequest.objects.filter(user=user, group=group).exists():
            messages.error(request, "You alreday have sent a request to this group (%s)" % group)
            return None
    
    for group in queryset:
        jrequest, created = JoinRequest.objects.get_or_create(user=user, group=group)
        if created:
            site = RequestSite(request)
            jrequest.send_creation_email(site)
            modeladmin.message_user(request, "Your join request has been sent (%s)" % group)
            modeladmin.log_change(request, group, "Requested to join this group.")
join_request.short_description = "Request to join the selected groups"
join_request.url_name = 'join-request'


@transaction.atomic
def enable_account(modeladmin, request, queryset):
    """
    The testbed operators can enable the users
    """
    
    # check if the selected user is alreday enabled
    for user in queryset:
        if user.is_active:
            messages.error(request, "This user is alreday active (%s)" % user)
            continue
        user.is_active = True
        user.save()
        modeladmin.message_user(request, "The user has been enabled (%s)" % user)
enable_account.short_description = "Enable selected users"


def confirm_send_email_view(modeladmin, request, queryset, subject, message):
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # The user has already confirmed
    if request.POST.get('post') == 'send_email_confirmation':
        form = ConfirmSendMailForm(request.POST)
        n = queryset.count()
        if n and form.is_valid():
            email_from = None
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            datatuple = []
            for user in queryset:
                datatuple.append((subject, message, email_from, [user.email]))
            send_mass_mail(datatuple)
            msg = "Message has been sent to %i users" % queryset.count()
            modeladmin.message_user(request, msg)
        # Return None to display the change list page again.
        return None
    
    if len(queryset) == 1:
        objects_name = force_text(opts.verbose_name)
    else:
        objects_name = force_text(opts.verbose_name_plural)
    
    form = ConfirmSendMailForm(initial={'subject': subject, 'message': message})
    context = {
        "title": "Are you sure?",
        "content_message": ("Are you sure you want to send the following message "
                            "to the selected %s?" % objects_name),
        "action_name": 'send_email',
        "action_value": 'send_email',
        "deletable_objects": queryset,
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'form': form,
        'subject': subject,
        'message': message,
    }
    
    # Display the confirmation page
    return TemplateResponse(request, 'admin/users/user/send_email_confirmation.html',
            context, current_app=modeladmin.admin_site.name)


def send_email(modeladmin, request, queryset):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = SendMailForm()
    if request.POST.get('post'):
        form = SendMailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            return confirm_send_email_view(modeladmin, request, queryset, subject, message)
        
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
send_email.verbose_name = 'Send email'

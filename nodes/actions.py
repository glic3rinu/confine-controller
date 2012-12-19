from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import router, transaction
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy, ugettext as _

from .forms import RequestCertificateForm


#TODO make this a generic pattern for reusing accros all actions that needs 
#     confirmation step


@transaction.commit_on_success
def reboot_selected(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Check that the user has change permission for the actual model
    if not modeladmin.has_change_permission(request):
        raise PermissionDenied
    
    using = router.db_for_write(modeladmin.model)
    
    # The user has already confirmed the reboot.
    if request.POST.get('post'):
        n = queryset.count()
        if n:
            for obj in queryset:
                obj.reboot()
                modeladmin.log_change(request, obj, "Instructed to reboot")
            msg = "%s selected nodes are instructed to reboot." % queryset.count()
            modeladmin.message_user(request, msg)
        # Return None to display the change list page again.
        return None
    
    if len(queryset) == 1:
        objects_name = force_text(opts.verbose_name)
    else:
        objects_name = force_text(opts.verbose_name_plural)
    
    context = {
        "title": "Are you sure?",
        "content_message": "Are you sure you want to reboot the selected nodes?",
        "action_name": 'Reboot',
        "deletable_objects": queryset,
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return TemplateResponse(request, 'admin/nodes/node/reboot_confirmation.html', 
        context, current_app=modeladmin.admin_site.name)

reboot_selected.short_description = ugettext_lazy("Reboot selected %(verbose_name_plural)s")


@transaction.commit_on_success
def request_cert(modeladmin, request, queryset):
    message = "Not implemented!"
    messages.warning(request, message)
    
    if queryset.count() != 1:
        messages.warning(request, "Please, one node at a time.")
        return
    
    node = queryset[0]
    form = RequestCertificateForm()
    
    # User has provided a pubkey
    if request.POST.get('post'):
        form = RequestCertificateForm(request.POST)
        if form.is_valid():
            pubkey = form.cleaned_data['pubkey']
            node.sign_cert_request(pubkey)
            modeladmin.log_change(request, node, "Certificate requested")
            return
        else:
            print form.errors
            
    
    node_url = reverse("admin:nodes_node_change", args=[node.pk])
    node_link = '<a href="%s">%s</a>' % (node_url, node)
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    context = {
        "title": "Request certificate for node '%s'" % node,
        "content_title": mark_safe("Request certificate for node '%s'" % node_link),
        "content_message": "Introduce the node certificate to be signed.",
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        "form": form,
    }
    
    # Display the confirmation page
    return TemplateResponse(request, 'admin/nodes/node/request_certificate.html', context, 
        current_app=modeladmin.admin_site.name)
    

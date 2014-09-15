from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import transaction
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

from controller.admin.decorators import action_with_confirmation

from .forms import RequestCertificateForm


@action_with_confirmation('reboot')
@transaction.atomic
def reboot_selected(modeladmin, request, queryset):
    # Check that the user has change permission for the actual model
    # performance improvement: if superuser skip
    if not request.user.is_superuser:
        for node in queryset:
            if not request.user.has_perm('nodes.change_node', node):
                msg = "You have not enought rights for rebooting the node '%s'!" % node
                modeladmin.message_user(request, msg, messages.ERROR)
                return None
    
    n = queryset.count()
    if n:
        for obj in queryset:
            obj.reboot()
            modeladmin.log_change(request, obj, "Instructed to reboot")
        msg = "%s selected nodes have been instructed to reboot." % n
        modeladmin.message_user(request, msg)
    
reboot_selected.short_description = ugettext_lazy("Reboot selected %(verbose_name_plural)s")
reboot_selected.url_name = 'reboot'
reboot_selected.verbose_name = u'Reboot\u2026'
reboot_selected.description = mark_safe('Restart this node to apply configuration changes.')


@transaction.atomic
def request_cert(modeladmin, request, queryset):
    if queryset.count() != 1:
        messages.warning(request, "Please, one node at a time.")
        return
    
    node = queryset.get()
    if not request.user.has_perm('nodes.change_node', node):
        raise PermissionDenied
    
    form = RequestCertificateForm()
    node_url = reverse("admin:nodes_node_change", args=[node.pk])
    node_link = '<a href="%s">%s</a>' % (node_url, node)
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    context = {
        "title": "Request certificate for node '%s'" % node,
        "content_title": mark_safe("Request certificate for node '%s'" % node_link),
        'queryset': queryset,
        'node': node,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # User has provided a CSR
    if request.POST.get('post'):
        form = RequestCertificateForm(request.POST)
        # form.node is needed in form.clean()
        form.node = node
        if form.is_valid():
            csr = form.cleaned_data['csr']
            signed_cert = node.mgmt_net.sign_cert_request(csr)
            context.update({'cert': signed_cert})
            return TemplateResponse(request, 'admin/nodes/node/show_certificate.html', context,
                current_app=modeladmin.admin_site.name)

    context['form'] = form
    # Display the confirmation page
    return TemplateResponse(request, 'admin/nodes/node/request_certificate.html', context, 
        current_app=modeladmin.admin_site.name)
request_cert.url_name = 'request-cert'
request_cert.verbose_name = u'Request certificate\u2026'
request_cert.description = mark_safe('Upload a node CSR to be signed by the '
                                     'testbed certificate authority (CA).')

from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import router, transaction
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

from .forms import OptionalFilesForm
from .models import Build, Config


# TODO implement an AJAX based feedback (triggering a refresh when there is an
#      state change should be enough)
#      build info in JSON format is available at <node_id>/firmware/build_info


@transaction.commit_on_success
def get_firmware(modeladmin, request, queryset):
    if queryset.count() != 1:
        messages.warning(request, "One node at a time")
        return
    
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    using = router.db_for_write(modeladmin.model)
    node = queryset[0]
    
    # Check if the user has permissions for download the image
    if not request.user.has_perm('nodes.getfirmware_node', node):
        raise PermissionDenied
    
    # User has requested a firmware build
    if request.POST.get('post'):
        form = OptionalFilesForm(request.POST)
        if form.is_valid():
            optional_fields = form.cleaned_data
            exclude = [ field for field, value in optional_fields.iteritems() if value ]
            build = Build.build(node, async=True, exclude=exclude)
            modeladmin.log_change(request, node, "Build firmware")
    
    context = {
        "action_name": 'Firmware',
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'node': node,
        'form': OptionalFilesForm(),
    }
    
    node_url = reverse("admin:nodes_node_change", args=[node.pk])
    node_link = '<a href="%s">%s</a>' % (node_url, node)
    
    try: build
    except NameError:
        try: build = Build.objects.get_current(node=node)
        except Build.DoesNotExist:
            context.update({
                "title": "Build firmware for '%s' Research Device" % node,
                "content_title":  mark_safe("Build firmware for '%s' Research Device" % node_link),
                "content_message": mark_safe("There is no pre-build up-to-date \
                    firmware for this research device, but you can instruct the \
                    system to build a fresh one for you, it will take only a few \
                    seconds."),
            })
            return TemplateResponse(request, 'admin/get_firmware.html', context, 
                current_app=modeladmin.admin_site.name)
    
    description = {
        Build.REQUESTED: "Build request received.",
        Build.QUEUED: "Build task queued for building.",
        Build.BUILDING: "Building image ...",
        Build.AVAILABLE: "Firmware available for download.",
        Build.DELETED: "This firmware is no longer available.",
        Build.OUTDATED: "This firmware is out-dated.",
        Build.FAILED: "The last building has failed. The error logs are monitored"
                      "and this issue will be fixed. But you can try again anyway.",
    }
    context.update({
        "title": "Research Device Firmware for '%s'" % node,
        "content_title": mark_safe("Research Device Firmware for '%s'" % node_link),
        "content_message": description[build.state],
        "build": build,
    })
    
    # Display the confirmation page
    return TemplateResponse(request, 'admin/get_firmware.html', context, 
        current_app=modeladmin.admin_site.name)

get_firmware.short_description = ugettext_lazy("Get firmware for selected %(verbose_name)s")

from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.admin import helpers
from django.db import router, transaction
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy, ugettext as _
#from firmware.tasks import generate_firmware
from firmware.models import FirmwareBuild, FirmwareConfig


#@transaction.commit_on_success
#def get_firmware(modeladmin, request, queryset):
#    message = "Not implemented!"
#    for node in queryset:
#        generate_firmware.delay(node)
#    messages.warning(request, message)


@transaction.commit_on_success
def get_firmware(modeladmin, request, queryset):
    if queryset.count() != 1:
        message.warning(request, "One node at a time")
        return
    
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Check that the user has change permission for the actual model
    if not modeladmin.has_change_permission(request):
        raise PermissionDenied
    
    using = router.db_for_write(modeladmin.model)
    
    node = queryset[0]
    
    # User has requested a firmware build
    if request.POST.get('post'):
        FirmwareBuild.build(node)
        modeladmin.log_change(request, node, "Build firmware")
        msg = 'Building firmware for your node "%s", this may take some time' % node.description
        modeladmin.message_user(request, msg)
        # Return None to display the change list page again.
        return None
    
    objects_name = force_text(opts.verbose_name)
    
    
    context = {
        "action_name": 'Firmware',
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'node': node,
    }
    
    try: build = FirmwareBuild.objects.get_current(node=node)
    except FirmwareBuild.DoesNotExist:
        context.update({
            "title": "Do you want to build a new firmware for your RD?",
            "content_message": """There is no available up-to-date firmware for 
                download, but I can build one for you and only will take a few seconds.
                Do you want me to build a new firwmare?""",
        })
    else:
        context.update({
            "title": "You can download a firmware for your research device",
            "content_message": "",
            "build": build
        })
    
    
    # Display the confirmation page
    return TemplateResponse(request, 'admin/get_firmware.html', 
        context, current_app=modeladmin.admin_site.name)

get_firmware.short_description = ugettext_lazy("Get firmware for selected %(verbose_name_plural)s")

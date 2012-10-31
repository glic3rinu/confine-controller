from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.admin import helpers
from django.db import router, transaction
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy, ugettext as _
from firmware.models import Build, Config


@transaction.commit_on_success
def get_firmware(modeladmin, request, queryset):
    if queryset.count() != 1:
        message.warning(request, "One node at a time")
        return
    
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Check if the user has change permission for the actual model
    if not modeladmin.has_change_permission(request):
        raise PermissionDenied
    
    using = router.db_for_write(modeladmin.model)
    node = queryset[0]
    
    # User has requested a firmware build
    if request.POST.get('post'):
        Build.build(node, async=True)
        modeladmin.log_change(request, node, "Build firmware")
        msg = 'Building firmware for node "%s", this may take some time' % node.description
        modeladmin.message_user(request, msg)
        return None
    
    context = {
        "action_name": 'Firmware',
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'node': node,
    }
    
    try: build = Build.objects.get_current(node=node)
    except Build.DoesNotExist:
        context.update({
            "title": 'Build firmware for "%s" Research Device?' % node.description,
            "content_message": mark_safe("""There is no pre-build up-to-date firmware for 
                this research device, but you can instruct the system to build a 
                fresh one for you, it will take only a few seconds. 
                <p> Do you want me to build a new firwmare?</p>"""),
        })
    else:
        context.update({
            "title": 'Research Device Firmware for "%s"' % node.description,
            "content_message": "",
            "build": build
        })
    
    # Display the confirmation page
    return TemplateResponse(request, 'admin/get_firmware.html', context, 
        current_app=modeladmin.admin_site.name)

get_firmware.short_description = ugettext_lazy("Get firmware for selected %(verbose_name_plural)s")

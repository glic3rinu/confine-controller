from django.contrib import messages
from django.contrib.admin import helpers
from django.db import transaction
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse

from .models import CnHost


@transaction.atomic
def cache_node_db(modeladmin, request, queryset):
    """
    Update CNDB cache for the selected nodes. This actions makes a
    query to resource specified at cndb_uri and updates the object
    data with the received response.
    + List of updated fields: arch, sliver_pub_{ipv6,ipv4,ipv4_range}, gis
    NOTE: manually defined data will be overrided
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    for node in queryset:
        if not request.user.has_perm('node.change_node', node):
            messages.error(request, "Sorry, you don't have enought privileges \
                for performing the requested action (cache node DB)")
            return None
    
    if request.POST.get('post'):
        errors = success = 0
        if queryset:
            #FIXME Ask user which fields want to update?
            for node in queryset:
                if node.cn is None:
                    continue
                try:
                    # TODO fields_to_update: arch, sliver_pub_{ipv6,ipv4,ipv4_range}
                    node.cn.cache_cndb('gis')
                except CnHost.CNDBFetchError as e:
                    errors += 1
                    modeladmin.log_change(request, node, "Error updating CNDB Cache: %s" % e)
                else:
                    success += 1
                    modeladmin.log_change(request, node, "Updated CNDB Cache")
        
        if errors:
            messages.error(request, "CNDB Cache update has failed for %d node(s). \
                See node history for details." % errors)
        if success:
            messages.info(request, "Updated CNDB Cache for %d node(s)" % success)
        else:
            messages.warning(request, "No nodes have been updated.")
        return None
    
    context = {
        "title": "Are you sure?",
        "content_message": "Are you sure you want to update CNDB cache of the selected nodes?",
        "action_name": 'Cache node DB',
        "action_value": 'cache_node_db',
        "deletable_objects": queryset,
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    # Display the confirmation page
    return TemplateResponse(request, 'admin/controller/generic_confirmation.html',
        context, current_app=modeladmin.admin_site.name)
cache_node_db.url_name = 'do-cache-cndb'
cache_node_db.verbose_name = u'Cache CNDB\u2026'
cache_node_db.description = mark_safe('Update this node with configuration stored on CNDB.')

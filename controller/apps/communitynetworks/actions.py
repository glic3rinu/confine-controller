from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.template.response import TemplateResponse

@transaction.commit_on_success
def cache_node_db(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    app_label = opts.app_label

    for node in queryset:
        if not request.user.has_perm('node.change_node', node):
            messages.error(request, "Sorry, you don't have enought privileges \
                for performing the requested action (cache node DB)")
            return None

    if request.POST.get('post'):
        n = queryset.count()
        if n:
            #FIXME ASK user which fields want to UPDATE??
            for node in queryset:
                _update_node(modeladmin, request, node)

        return None

    context = {
        "title": "Are you sure?",
        "content_message": "Are you sure you want to update cache of the selected nodes using node DB?",
        "action_name": 'Cache node DB',
        "action_value": 'cache_node_db_selected',
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
cache_node_db.verbose_name = 'Cache CNDB'

def _update_node(modeladmin, request, node):
    # check if uri is defined
    if not node.cn.exists() or not node.cn.get().cndb_uri:
        return # nothing to do cause there are not CN host relationated

    # query the cndb
    cn = node.cn.get()
    cache = cn.get_cache()

    if cache.get('error'):
        messages.error(request, cache.get('text'))
        return

    json = cache.get('text')

    #### NODE specific STAFF ####
    # fields_to_update: arch, sliver_pub_{ipv6,ipv4,ipv4_range}, gis
    # select the desired data from the jsonized data # TODO how to define which?
    pos = json.get('attributes').get('position')
    lat, lon = pos.get('lat'), pos.get('lon')

    # update the node info
    try:
        node.gis # exist related object?
    except ObjectDoesNotExist:
        from gis.models import NodeGeolocation
        node.gis = NodeGeolocation()
        
    node.gis.geolocation = "%s,%s" % (lat, lon)
    node.gis.save()
    node.save()

    messages.info(request, "Updated CNDB Cache of node '%s'" % node)
    modeladmin.log_change(request, node, "Updated CNDB Cache")

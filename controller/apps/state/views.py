import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from users.models import Group
from .helpers import get_report_data, get_node_version_data

def report_view(request):
    """ Testbed report status view """
    template = 'admin/state/state/report.html'
    iframe = request.GET.get("iframe", False)
    opt = {
        'data': get_report_data(),
        'node_sw': get_node_version_data(),
        'iframe': iframe,
    }
    context = RequestContext(request)
    return render_to_response(template, opt, context_instance=context)

def slices_view(request):
    """ Testbed slices status view """
    template = 'admin/state/state/slices.html'
    iframe = request.GET.get("iframe", False)
    opt = {
        'iframe': iframe,
    }
    context = RequestContext(request)
    return render_to_response(template, opt, context_instance=context)

def slivers_view(request):
    """ Testbed slivers status view """
    template = 'admin/state/state/slivers.html'
    iframe = request.GET.get("iframe", False)
    opt = {
        'iframe': iframe,
    }
    context = RequestContext(request)
    return render_to_response(template, opt, context_instance=context)

def get_slices_data(request):
    """ 
    Generate JSON containing numbers of slivers for slices
    grouped by groups
    """
    slc_data = []
    for group in Group.objects.all():
        # init structs
        slices_count = group.slices.count()
        group_data = {
            'name': "Group: %s (%s slices)" % (group.name, slices_count),
            'uri': reverse('admin:users_group_change', args=(group.id,)),
        }
        group_slices = []
        
        # get group slices info
        for slice in group.slices.all():
            group_slices.append({
                'name': slice.name,
                'uri':  reverse('admin:slices_slice_change', args=(slice.id,)),
                'size': slice.slivers.count(),
            })
            
        # append based on dj3s structure
        if slices_count > 0:
            group_data['children'] = group_slices
        else:
            group_data['size'] = slices_count
        
        ## append to the global data
        slc_data.append(group_data)

    response_data = json.dumps({
        'name': "Community-Lab.net",
        'children' : slc_data,
    })
    return HttpResponse(response_data, content_type="application/json")

def get_slivers_data(request):
    """ 
    Generate JSON containing numbers of slivers for slices
    grouped by nodes
    """
    slc_data = []
    for group in Group.objects.all():
        # init structs
        nodes_count = group.nodes.count()
        group_nodes = []
        
        # get group slices info
        for node in group.nodes.all():
            if node.slivers.count() == 0:
                g_slices = ''
            else:
                g_slices = ", ".join([slv.slice.name for slv in node.slivers.all()])
            group_nodes.append({
                'name': node.name,
                'uri':  reverse('admin:nodes_node_change', args=[node.id]),
                'size': node.slivers.count(),
                'slices': g_slices
            })
        
        ## append to the global data
        slc_data.append({
            'name': "Group: %s (%s nodes)" % (group.name, nodes_count),
            'children': group_nodes,
            'uri': reverse('admin:users_group_change', args=(group.id,)),
        })

    response_data = json.dumps({
        'name': "Community-Lab.net",
        'children' : slc_data,
    })
    return HttpResponse(response_data, content_type="application/json")

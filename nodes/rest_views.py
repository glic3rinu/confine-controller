# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.utils import simplejson

from nodes import settings

from nodes import models as node_models

from slices import models as slice_models

def testbed(request):
    response_dict = {
        'api_version': settings.API_VERSION,
        'params': {
            'mgmt_ipv6_prefix': settings.MGMT_IPV6_PREFIX,
            'priv_ipv4_prefix_dflt': settings.PRIV_IPV4_PREFIX_DFLT,
            'sliver_mac_prefix_dflt': settings.SLIVER_MAC_PREFIX_DFLT
            },
        'server': "https://%s/confine/server/" % (
                    settings.TESTBED_BASE_IP,
                    ),
        'nodes': "https://%s/confine/nodes/" % (
                    settings.TESTBED_BASE_IP,
                    ),
        'slices': "https://%s/confine/slices/" % (
                    settings.TESTBED_BASE_IP,
                    ),
        'slivers': "https://%s/confine/slivers/" % (
                    settings.TESTBED_BASE_IP,
                    ),
        'users': "https://%s/confine/users/" % (
                    settings.TESTBED_BASE_IP,
                    ),
        'gateways': "https://%s/confine/gateways/" % (
                    settings.TESTBED_BASE_IP,
                    ),
        'hosts': "https://%s/confine/hosts/" % (
                    settings.TESTBED_BASE_IP,
                    ),
        'templates': "https://%s/confine/templates/" % (
                    settings.TESTBED_BASE_IP,
                    ),
        'islands': "https://%s/confine/islands/" % (
                    settings.TESTBED_BASE_IP,
                    )
        }
    
    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def server(request):
    response_dict = {
        'api_version': settings.API_VERSION,
        'cn_url': settings.SERVER_URL,
        'tinc_name': settings.SERVER_NAME,
        'tinc_pubkey': settings.SERVER_PUBLIC_KEY,
        'tinc_connect_to': [],
        'tinc_addresses': [],
        }
    
    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def node_list(request):
    response_dict = {}
    response_dict['api_version'] = settings.API_VERSION
    response_dict['nodes'] = []

    nodes = node_models.Node.objects.all()
    for node in nodes:
        response_dict['nodes'].append(
            {
                'id': node.id,
                'action': node.action,
                'href': "https://%s/confine/nodes/%i/" % (
                    settings.TESTBED_BASE_IP,
                    node.id
                    )
                }
            )

    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def slice_list(request):
    response_dict = {}
    response_dict['api_version'] = settings.API_VERSION
    response_dict['slices'] = []

    slices = slice_models.Slice.objects.all()
    for sl in slices:
        response_dict['slices'].append(
            {
                'id': sl.id,
                'href': "https://%s/confine/slices/%i/" % (
                    settings.TESTBED_BASE_IP,
                    sl.id
                    )
                }
            )

    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def single_node(request, node_id):
    node = node_models.Node.objects.get(id = node_id)
    response_dict = {
        'api_version': settings.API_VERSION,
        'id': node.id,
        'rd_arch': node.architecture,
        'rd_public_ipv4_total': node.rd_public_ipv4_total,
        'priv_ipv4_prefix': node.priv_ipv4_prefix,
        'sliver_mac_prefix': node.sliver_mac_prefix,
        'action': node.action,
        'direct_ifaces': [],
        'cn_url': node.url,
        'tinc_name': "node_%i" % node.id,
        'tinc_pubkey': node.public_key,
        'tinc_connect_to': [],
        'islands': [],
        'admin': {'id': node.owner.id,
                  'href': "https://%s/confine/users/%i/" % (
                      settings.TESTBED_BASE_IP,
                      node.owner.id
                      )
                  },
        'slivers': [],
        'base_url': "https://%s/confine/" % (
                settings.TESTBED_BASE_IP,
                )
        }


    for iface in node.interface_set.all():
        response_dict['direct_ifaces'].append(
            {
                'name': iface.name,
                'channel': iface.channel,
                'essid': iface.essid
                }
            )


    for island in node.island.all():
        response_dict['islands'].append(
            {
                'id': island.id,
                'name': island.name,
                'href': "https://%s/confine/islands/%i/" % (
                    settings.TESTBED_BASE_IP,
                    island.id
                    )
                }
            )
    for sliver in node.sliver_set.all():
        response_dict['slivers'].append(
            {
                'slice': sliver.slice.id,
                'href': "https://%s/confine/slivers/%i-%i/" % (
                    settings.TESTBED_BASE_IP,
                    node.id,
                    sliver.slice.id
                    )
                }
            )



    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def single_slice(request, slice_id):
    sl = slice_models.Slice.objects.get(id = slice_id)
    template = sl.template
    response_dict = {
        'api_version': settings.API_VERSION,
        'id': sl.id,
        'alias': sl.name,
        'vlan_nr': sl.vlan_nr,
        'template': {
            'id': template.id if template else -1,
            'arch': template.arch if template else "",
            'href': "https://%s/confine/templates/%i/" % (
                    settings.TESTBED_BASE_IP,
                    slice.id,
                    ) if template else ""
            },
        'exp_data_uri': sl.exp_data_uri,
        'exp_data_sha256': sl.exp_data_sha256,
        'action': sl.action,
        'users': [],
        'slivers': [],
        }
    response_dict['users'].append(
        {
            'id': sl.user.id,
            'pub_key': sl.user.get_profile().ssh_key,
            'href': "https://%s/confine/users/%i/" % (
                    settings.TESTBED_BASE_IP,
                    sl.user.id,
                    )
            }
        )
    if sl.research_group:
        for user in slice.research_group.users.all():
            response_dict['users'].append(
                {
                    'id': user.id,
                    'pub_key': user.get_profile().ssh_key,
                    'href': "https://%s/confine/users/%i/" % (
                        settings.TESTBED_BASE_IP,
                        user.id,
                        )
                    }
                )
    for sliver in sl.sliver_set.all():
        response_dict['slivers'].append(
            {
                'node': sliver.node.id,
                'href': "https://%s/confine/slivers/%i-%i/" % (
                    settings.TESTBED_BASE_IP,
                    sliver.node.id,
                    sliver.slice.id
                    )
                }
            )
    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def sliver_list(request):
    slivers = slice_models.Sliver.objects.all()

    response_dict = {
        'api_version': settings.API_VERSION,
        'slivers': []
        }

    for sliver in slivers:
        response_dict['slivers'].append(
            {
                'node': sliver.node.id,
                'slice': sliver.slice.id,
                'href': "https://%s/confine/slivers/%i-%i/" % (
                    settings.TESTBED_BASE_IP,
                    sliver.node.id,
                    sliver.slice.id
                    )
                }
            )
    
    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def single_sliver(request, sliver_id):
    node_id, slice_id = sliver_id.split("-")
    sliver = slice_models.Sliver.objects.get(node__id = node_id,
                                             slice__id = slice_id)
    response_dict = {
        'api_version': settings.API_VERSION,
        'slice':{
            'id': sliver.slice.id,
            'href': "https://%s/confine/slices/%i/" % (
                    settings.TESTBED_BASE_IP,
                    sliver.slice.id
                    )
            },
        'node': {
            'id': sliver.node.id,
            'href': "https://%s/confine/nodes/%i/" % (
                    settings.TESTBED_BASE_IP,
                    sliver.node.id
                    )
            },
        'interfaces': []
        }
    for nr in sliver.networkrequest_set.all():
        if nr.interface:
            response_dict['interfaces'].append(
                {
                    'name': nr.interface.name,
                    'type': nr.type,
                    'use_default_gw': "",
                    'parent_name': ""
                    }
                )
    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def template_list(request):
    templates = slice_models.SliverTemplate.objects.all()
    response_dict = {
        'api_version': settings.API_VERSION,
        'templates': []
        }
    for template in templates:
        response_dict['templates'].append(
            {
                'id': template.id,
                'name': template.name,
                'href': "https://%s/confine/templates/%i/" % (
                    settings.TESTBED_BASE_IP,
                    template.id
                    )
                }
            )
    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def single_template(request, template_id):
    template = slice_models.SliverTemplate.objects.get(id = template_id)
    response_dict = {
        'api_version': settings.API_VERSION,
        'id': template.id,
        'name': template.name,
        'type': template.template_type,
        'arch': template.arch,
        'enabled': template.enabled,
        'data_uri': template.data_uri,
        'data_sha256': template.data_sha256
        }
    
    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def island_list(request):
    islands = node_models.Island.objects.all()
    response_dict = {
        'api_version': settings.API_VERSION,
        'islands': []
        }

    for island in islands:
        response_dict['islands'].append(
            {
                'id': island.id,
                'name': island.name,
                'href': "https://%s/confine/islands/%i/" % (
                    settings.TESTBED_BASE_IP,
                    island.id
                    )
                }
            )
    
    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def single_island(request, island_id):
    island = node_models.Island.objects.get(id = island_id)
    response_dict = {
        'api_version': settings.API_VERSION,
        'id': island.id,
        'name': island.name
        }
    
    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

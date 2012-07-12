# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.utils import simplejson

from nodes import settings

from nodes import models as node_models

from slices import models as slice_models

def testbed(request):
    pass

def node_list(request):
    response_dict = {}
    response_dict['api_version'] = settings.API_VERSION
    response_dict['nodes'] = []

    nodes = node_models.Node.objects.all()
    for node in nodes:
        response_dict['nodes'].append(
            {
                'id': node.id,
                'action': "",
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

def node(request, node_id):
    node = node_models.Node.objects.get(id = node_id)
    response_dict = {
        'api_version': settings.API_VERSION,
        'id': node.id,
        'rd_arch': node.architecture,
        'rd_public_ipv4_total': "",
        'priv_ipv4_prefix': "",
        'sliver_mac_prefix': "",
        'action': "",
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

    if node.island:
        response_dict['islands'].append(
            {
                'id': node.island.id,
                'name': node.island.name,
                'href': "https://%s/confine/islands/%i/" % (
                    settings.TESTBED_BASE_IP,
                    node.island.id
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

# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.utils import simplejson

from nodes import settings

from nodes import models


def testbed(request):
    pass

def node_list(request):
    response_dict = {}
    response_dict['api_version'] = settings.API_VERSION
    response_dict['nodes'] = []

    nodes = models.Node.objects.all()
    for node in nodes:
        node_item = {
            'id': node.id,
            'action': "",
            'href': "https://%s/confine/nodes/%i/" % (
                settings.TESTBED_BASE_IP,
                node.id
                )
            }
        response_dict['nodes'].append(node_item)

    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

def node(request, node_id):
    response_dict = {}

    return HttpResponse(
        simplejson.dumps(response_dict),
        mimetype="application/json"
        )

# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from xml.etree import ElementTree
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt

from nodes import settings
from nodes import models as node_models
from nodes import utils
from nodes import forms

from slices import models as slice_models
# XML ONLY

@csrf_exempt
def upload_node(request):
    """
    Upload node function. POST request. Set to PROJECTED state
    Input format:
    <xml>
    <node>
    <hostname>hostname</hostname>
    <url>url</url>
    <architecture>architecture</architecture>
    </node>
    Output format:
    <xml>
    <response>
    <node_created>status</node_created>
    </response>

    Status:
    1 -> ok
    0 -> problem
    """
    node_created = 0
    if request.method == "POST":
        raw_xml = request.POST.get("node_data", None)
        tree = ElementTree.fromstring(raw_xml)
        hostname = tree.find('hostname').text
        url = tree.find('url').text
        architecture = tree.find('architecture').text
        # TODO: complete parse tree
        node = node_models.Node(hostname = hostname,
                                url = url,
                                architecture = architecture,
                                status = settings.PROJECTED)
        node.save()
        node_created = 1
    return render_to_response("public/xml/upload_node.xml",
                              RequestContext(request,
                                             {
                                                 'node_created': node_created,
                                                 }
                                             )
                              )

def delete_node(request):
    """
    Delete request for node X
    Input format:
    <xml>
    <node>
    <hostname>hostname</hostname>
    </node>
    Output format:
    <xml>
    <response>
    <delete_request>status</delete_request>
    </response>

    Status:
    1 -> ok
    0 -> problem
    """
    node_deleted = 0
    if request.method == "POST":
        raw_xml = request.POST.get("node_data", None)
        tree = ElementTree.fromstring(raw_xml)
        hostname = tree.find('hostname').text

        try:
            node = node_models.Node.objects.get(hostname = hostname)
            delete_request = node_models.DeleteRequest(node = node)
            delete_request.save()
            node_deleted = 1
        except:
            pass
    return render_to_response("public/xml/delete_node.xml",
                              RequestContext(request,
                                             {
                                                 'node_deleted': node_deleted,
                                                 }
                                             )
                              )

def get_node_configuration(request):
    """
    Retrieve the node configuration file
    Input format:
    <xml>
    <node>
    <hostname>hostname</hostname>
    </node>
    Output format:
    <xml>
    <response>
    <config_request>status</config_request>
    <node_config>config</node_config>
    </response>

    Status:
    1 -> ok
    0 -> problem
    """
    hostname_found = 0
    config = ""
    if request.method == "POST":
        raw_xml = request.POST.get("node_data", None)
        tree = ElementTree.fromstring(raw_xml)
        hostname = tree.find('hostname').text

        try:
            node = node_models.Node.objects.get(hostname = hostname)
            config = utils.load_node_config(node)
            hostname_found = 1
        except:
            pass
    return render_to_response("public/xml/get_node_configuration.xml",
                              RequestContext(request,
                                             {
                                                 'hostname_found': hostname_found,
                                                 'config': config
                                                 }
                                             )
                              )

def get_node_public_keys(request):
    """
    Retrieve public keys of node users
    <xml>
    <node>
    <hostname>hostname</hostname>
    </node>
    Output format:
    <xml>
    <response>
    <key_request>status</config_request>
    <node_keys>
    <node_key>key</node_key>
    <node_key>key</node_key>
    </node_keys>
    </response>

    Status:
    1 -> ok
    0 -> problem
    """
    hostname_found = 0
    keys = []
    if request.method == "POST":
        raw_xml = request.POST.get("node_data", None)
        tree = ElementTree.fromstring(raw_xml)
        hostname = tree.find('hostname').text

        try:
            node = node_models.Node.objects.get(hostname = hostname)
            keys.append(node.public_key)
            hostname_found = 1
        except:
            pass
    return render_to_response("public/xml/get_node_keys.xml",
                              RequestContext(request,
                                             {
                                                 'hostname_found': hostname_found,
                                                 'keys': keys
                                                 }
                                             )
                              )
    

# HTML (XML SOON)
def index(request):
    """
    Shows index dashboard
    """
    return render_to_response("public/index.html",
                              RequestContext(request,
                                             {
                                                 
                                                 }
                                             )
                              )

def node_index(request):
    """
    Shows all available nodes
    """
    nodes = node_models.Node.objects.all()
    return render_to_response("public/node_index.html",
                              RequestContext(request,
                                             {
                                                 'nodes': nodes
                                                 }
                                             )
                              )

@login_required
def create_slice(request):
    """
    Create a new slice for the given nodes
    """
    if request.method == "POST":
        form = forms.NewSliceForm(request.POST)
        if form.is_valid():
            c_data = form.cleaned_data
            nodes = c_data.get('nodes', [])
            if len(nodes) > 0:
                c_slice = slice_models.Slice(name = c_data.get('name'),
                                             user = request.user,)
                c_slice.save()
                for node in nodes:
                    c_node = node_models.Node.objects.get(id = node)
                    c_sliver = slice_models.Sliver(slice = c_slice,
                                                   node = c_node)
                    c_sliver.save()
                return HttpResponseRedirect("/show_own_slices/")
            
    else:
        form = forms.NewSliceForm()
    return render_to_response("public/create_slice.html",
                              RequestContext(request,
                                             {
                                                 'form': form,
                                                 }
                                             )
                              )

@login_required
def show_own_slices(request):
    """
    Shows all user slices
    """
    slices = request.user.slice_set.all()
    return render_to_response("public/show_own_slices.html",
                              RequestContext(request,
                                             {
                                                 'slices': slices
                                                 }
                                             )
                              )

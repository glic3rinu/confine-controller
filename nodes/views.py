# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from xml.etree import ElementTree
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt

from nodes import settings
from nodes import models as node_models
from nodes import node_utils as utils
from nodes import forms

from slices import models as slice_models

from nodes import api
# XML ONLY

@csrf_exempt
def upload_node_xml(request):
    """
    Upload node function. POST request. Set to PROJECTED state
    Input format:
    <xml>
    <node>
    <hostname>hostname</hostname>
    <ip>ip</ip>
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
        params = utils.extract_params(tree, ['hostname', 'ip', 'architecture'])
        if api.create_node(params):
            node_created = 1
    return render_to_response("public/xml/upload_node.xml",
                              RequestContext(request,
                                             {
                                                 'node_created': node_created,
                                                 }
                                             )
                              )

def delete_node_xml(request):
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
        params = utils.extract_params(tree, ['hostname'])
        if api.delete_node(params):
            node_deleted = 1 

    return render_to_response("public/xml/delete_node.xml",
                              RequestContext(request,
                                             {
                                                 'node_deleted': node_deleted,
                                                 }
                                             )
                              )

def get_node_configuration_xml(request):
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
        config = api.get_node_configuration({'hostname': hostname})
        if config != None:
            hostname_found = 1
        
    return render_to_response("public/xml/get_node_configuration.xml",
                              RequestContext(request,
                                             {
                                                 'hostname_found': hostname_found,
                                                 'config': config
                                                 }
                                             )
                              )

def get_node_public_keys_xml(request):
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
        keys = api.get_node_public_keys({'hostname': hostname})
        if keys != None:
            hostname_found = 1
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
            if api.create_slice({
                'nodes': nodes,
                'user': request.user,
                'name': c_data.get('name')
                }):
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
    slices = api.show_slices({'user': request.user})
    return render_to_response("public/show_own_slices.html",
                              RequestContext(request,
                                             {
                                                 'slices': slices
                                                 }
                                             )
                              )

@login_required
def upload_node(request):
    """
    Create a new node
    """
    if request.method == "POST":
        form = forms.NodeForm(request.POST)
        if form.is_valid():
            c_data = form.cleaned_data
            data = {
                'hostname': c_data.get('hostname'),
                'ip': c_data.get('ip'),
                'architecture': c_data.get('architecture')
                    }
            if api.create_node(data):
                return HttpResponseRedirect("/node_index/")
    else:
        form = forms.NodeForm()
    return render_to_response("public/upload_node.html",
                              RequestContext(request,
                                             {
                                                 'form': form,
                                                 }
                                             )
                              )

@login_required
def delete_node(request):
    """
    Create a new delete request for a node
    """
    if request.method == "POST":
        form = forms.DeleteRequestForm(request.POST)
        if form.is_valid():
            c_data = form.cleaned_data
            data = {
                'hostname': c_data.get('node').hostname,
                    }
            if api.delete_node(data):
                return HttpResponseRedirect("/node_index/")
    else:
        form = forms.DeleteRequestForm()
    return render_to_response("public/delete_node.html",
                              RequestContext(request,
                                             {
                                                 'form': form,
                                                 }
                                             )
                              )

@login_required
def get_node_configuration(request, node_hostname):
    """
    Displays the current node configuration
    """
    config = api.get_node_configuration({'hostname': node_hostname})
    return render_to_response("public/get_node_configuration.html",
                              RequestContext(request,
                                             {
                                                 'config': config,
                                                 }
                                             )
                              )

@login_required
def get_node_public_keys(request, node_hostname):
    """
    Displays all node related keys
    """
    keys = api.get_node_public_keys({'hostname': node_hostname})
    return render_to_response("public/get_node_public_keys.html",
                              RequestContext(request,
                                             {
                                                 'keys': keys,
                                                 }
                                             )
                              )

@login_required
def get_slice_public_keys(request, slice_name):
    """
    Displays all node related keys
    """
    keys = api.get_slice_public_keys({'name': slice_name})
    return render_to_response("public/get_slice_public_keys.html",
                              RequestContext(request,
                                             {
                                                 'keys': keys,
                                                 }
                                             )
                              )

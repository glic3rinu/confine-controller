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
from slices import forms as slices_forms

from nodes import api

from django.forms.models import modelformset_factory

from django.contrib import messages

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
    <id>id</id>
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
        params = utils.extract_params(tree, ['id'])
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
    <id>id</id>
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
        id = tree.find('id').text
        config = api.get_node_configuration({'id': id})
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
    <id>id</id>
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
        id = tree.find('id').text
        keys = api.get_node_public_keys({'id': id})
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
    nodes = api.get_nodes()
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
    NetworkFormset = modelformset_factory(slice_models.NetworkRequest,
                                          extra = 1,
                                          form = slices_forms.NetworkRequestForm)
    if request.method == "POST":
        form = forms.NewSliceForm(request.POST)
        form.fields['nodes'].choices = map(lambda a: [a.id, a.hostname], api.get_nodes())
        if form.is_valid():
            c_data = form.cleaned_data
            nodes = c_data.get('nodes', [])
            node_info = {}
            node_widget = form.fields.get('nodes').widget
            for node_id in nodes:
                network = NetworkFormset(request.POST,
                                         prefix = "node_%s_nr" % node_id)
                node_widget.set_retented_data(node_id,
                                              'network',
                                              network)
                cpu = slices_forms.CPURequestForm(request.POST,
                                                  prefix = "node_%s_c" % node_id)
                node_widget.set_retented_data(node_id,
                                              'cpu',
                                              cpu)
                storage = slices_forms.StorageRequestForm(request.POST,
                                                          prefix = "node_%s_s" % node_id)
                node_widget.set_retented_data(node_id,
                                              'storage',
                                              storage)
                memory = slices_forms.MemoryRequestForm(request.POST,
                                                        prefix = "node_%s_m" % node_id)
                node_widget.set_retented_data(node_id,
                                              'memory',
                                              memory)
                child_networks = []
                child_cpu = None
                child_storage = None
                child_memory = None
                if network.is_valid():
                    child_networks = network.save(commit = False)
                if cpu.is_valid():
                    child_cpu = cpu.save(commit = False)
                if storage.is_valid():
                    child_storage = storage.save(commit = False)
                if memory.is_valid():
                    child_memory = memory.save(commit = False)
                node_info[node_id] = {'networks': child_networks,
                                      'cpu': child_cpu,
                                      'storage': child_storage,
                                      'memory': child_memory}
                
            if api.create_slice({
                'nodes': node_info,
                'user': request.user,
                'name': c_data.get('name')
                }):
                messages.info(request, "Slice created")
                return HttpResponseRedirect("/show_own_slices/")
        messages.info(request, "A problem arised when creating slice")    
    else:
        form = forms.NewSliceForm()
        form.fields['nodes'].choices = map(lambda a: [a.id, a.hostname], api.get_nodes())
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
    InterfaceFormset = modelformset_factory(node_models.Interface,
                                            extra = 1,
                                            form = forms.InterfaceForm)
    
    if request.method == "POST":
        node_form = forms.NodeForm(request.POST, prefix = "node")
        storage_form = forms.StorageForm(request.POST,prefix = "storage")
        memory_form = forms.MemoryForm(request.POST,prefix = "memory")
        cpu_form = forms.CPUForm(request.POST,prefix = "cpu")
        interface_formset = InterfaceFormset(request.POST, prefix = "interfaces")
                                             
        if node_form.is_valid() and storage_form.is_valid() and memory_form.is_valid() and cpu_form.is_valid() and interface_formset.is_valid():

            node = node_form.save(commit = False)
            storage = storage_form.save(commit = False)
            memory = memory_form.save(commit = False)
            cpu = cpu_form.save(commit = False)
            interfaces = interface_formset.save(commit = False)
            data = {
                'node': node,
                'storage': storage,
                'memory': memory,
                'cpu': cpu,
                'interfaces': interfaces
                    }
            if api.set_node(data):
                messages.info(request, "Node uploaded successfuly")
                return HttpResponseRedirect("/node_index/")
        messages.info(request, "A problem arised while uploading node")
    else:
        node_form = forms.NodeForm(prefix = "node")
        storage_form = forms.StorageForm(prefix = "storage")
        memory_form = forms.MemoryForm(prefix = "memory")
        cpu_form = forms.CPUForm(prefix = "cpu")
        interface_formset = InterfaceFormset(prefix = "interfaces",
                                             queryset = node_models.Interface.objects.none())
        
    return render_to_response("public/upload_node.html",
                              RequestContext(request,
                                             {
                                                 'node_form': node_form,
                                                 'storage_form': storage_form,
                                                 'memory_form': memory_form,
                                                 'cpu_form': cpu_form,
                                                 'interface_formset': interface_formset
                                                 }
                                             )
                              )

@login_required
def edit_node(request, node_id):
    """
    Edit and update a given node
    """
    InterfaceFormset = modelformset_factory(node_models.Interface,
                                            extra = 1,
                                            form = forms.InterfaceForm)

    node = api.get_node({'id': node_id})
    if node:
        if request.method == "POST":
            node_form = forms.NodeForm(request.POST,
                                       prefix = "node",
                                       instance = node)
            try:
                storage_form = forms.StorageForm(request.POST,
                                                 prefix = "storage",
                                                 instance = node.storage)
            except:
                storage_form = forms.StorageForm(request.POST,
                                                 prefix = "storage")

            try:
                memory_form = forms.MemoryForm(request.POST,
                                               prefix = "memory",
                                               instance = node.memory)
            except:
                memory_form = forms.MemoryForm(request.POST,
                                               prefix = "memory")

            try:
                cpu_form = forms.CPUForm(request.POST,
                                         prefix = "cpu",
                                         instance = node.cpu)
            except:
                cpu_form = forms.CPUForm(request.POST,
                                         prefix = "cpu")
            
            interface_formset = InterfaceFormset(request.POST,
                                                 prefix = "interfaces")
                                             
            if node_form.is_valid() and storage_form.is_valid() and memory_form.is_valid() and cpu_form.is_valid() and interface_formset.is_valid():

                node = node_form.save(commit = False)
                storage = storage_form.save(commit = False)
                memory = memory_form.save(commit = False)
                cpu = cpu_form.save(commit = False)
                interfaces = interface_formset.save(commit = False)
                data = {
                    'node': node,
                    'storage': storage,
                    'memory': memory,
                    'cpu': cpu,
                    'interfaces': interfaces
                    }
                if api.edit_node(data):
                    messages.info(request, "Node updated successfuly")
                    return HttpResponseRedirect("/node_index/")
            messages.info(request, "A problem arised while updating node")
        else:
            node_form = forms.NodeForm(prefix = "node",
                                       instance = node)
            try:
                storage_form = forms.StorageForm(prefix = "storage",
                                                 instance = node.storage)
            except:
                storage_form = forms.StorageForm(prefix = "storage")
            try:
                memory_form = forms.MemoryForm(prefix = "memory",
                                               instance = node.memory)
            except:
                memory_form = forms.MemoryForm(prefix = "memory")
            try:
                cpu_form = forms.CPUForm(prefix = "cpu",
                                         instance = node.cpu)
            except:
                cpu_form = forms.CPUForm(prefix = "cpu")
            interface_formset = InterfaceFormset(prefix = "interfaces",
                                                 queryset = node_models.Interface.objects.filter(node = node))
        return render_to_response("public/edit_node.html",
                                  RequestContext(request,
                                                 {
                                                     'node_form': node_form,
                                                     'storage_form': storage_form,
                                                     'memory_form': memory_form,
                                                     'cpu_form': cpu_form,
                                                     'interface_formset': interface_formset
                                                     }
                                                 )
                                  )
    else:
        return HttpResponseRedirect("/")

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
                'id': c_data.get('node').id,
                    }
            if api.delete_node(data):
                messages.info(request, "Delete request created successfuly")
                return HttpResponseRedirect("/node_index/")
        messages.info(request, "A problem arised while creating delete request")
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
def get_node_configuration(request, node_id):
    """
    Displays the current node configuration
    """
    config = api.get_node_configuration({'id': node_id})
    return render_to_response("public/get_node_configuration.html",
                              RequestContext(request,
                                             {
                                                 'config': config,
                                                 }
                                             )
                              )

@login_required
def get_node_public_keys(request, node_id):
    """
    Displays all node related keys
    """
    keys = api.get_node_public_keys({'id': node_id})
    return render_to_response("public/get_node_public_keys.html",
                              RequestContext(request,
                                             {
                                                 'keys': keys,
                                                 }
                                             )
                              )

@login_required
def get_slice_public_keys(request, slice_slug):
    """
    Displays all node related keys
    """
    keys = api.get_slice_public_keys({'slug': slice_slug})
    return render_to_response("public/get_slice_public_keys.html",
                              RequestContext(request,
                                             {
                                                 'keys': keys,
                                                 }
                                             )
                              )

@login_required
def delete_slice(request, slice_slug):
    """
    Delete the given slice
    """
    if api.delete_slices({"slice_slug": slice_slug}):
        messages.info(request, "Slice deleted successfuly")
    else:
        messages.info(request, "An error appeared on deleting the given slice")
    return HttpResponseRedirect("/show_own_slices/")

@login_required
def deploy_slivers(request, slice_slug):
    """
    Deploy all slivers for a given slice
    """
    keys = api.deploy_slivers({'slice_slug': slice_slug})
    messages.info(request, "Deploy sliver task started")
    return HttpResponseRedirect("/show_own_slices/")

@login_required
def start_sliver(request, sliver_id):
    """
    Start the given sliver
    """
    keys = api.start_slivers({'sliver_id': sliver_id})
    messages.info(request, "Start sliver task started")
    return HttpResponseRedirect("/show_own_slices/")

@login_required
def stop_sliver(request, sliver_id):
    """
    Stop the given sliver
    """
    keys = api.stop_slivers({'sliver_id': sliver_id})
    messages.info(request, "Stop sliver task started")
    return HttpResponseRedirect("/show_own_slices/")

@login_required
def delete_sliver(request, sliver_id):
    """
    Delete the given sliver
    """
    if api.delete_slivers({"sliver_id": sliver_id}):
        messages.info(request, "Sliver deleted successfuly")
    else:
        messages.info(request, "An error appeared on deleting the given sliver")
    return HttpResponseRedirect("/show_own_slices/")

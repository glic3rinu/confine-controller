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
    IsolatedifaceFormset = modelformset_factory(slice_models.IsolatedIface,
                                              extra = 1,
                                              form = slices_forms.IsolatedIfaceForm)
    PublicIfaceFormset = modelformset_factory(slice_models.PublicIface,
                                              extra = 1,
                                              form = slices_forms.PublicIfaceForm)
    PrivateIfaceFormset = modelformset_factory(slice_models.PrivateIface,
                                              extra = 1,
                                              form = slices_forms.PrivateIfaceForm)
    
    if request.method == "POST":
        form = forms.NewSliceForm(request.POST)
        form.fields['nodes'].choices = map(lambda a: [a.id, a.hostname], api.get_nodes())
        if form.is_valid():
            c_data = form.cleaned_data
            nodes = c_data.get('nodes', [])
            node_info = {}
            node_widget = form.fields.get('nodes').widget
            for node_id in nodes:
                ii = IsolatedifaceFormset(request.POST,
                                          prefix = "node_%s_ii" % node_id)
                node_widget.set_retented_data(node_id,
                                              'isolatediface',
                                              ii)
                pubi = PublicIfaceFormset(request.POST,
                                          prefix = "node_%s_pubi" % node_id)
                node_widget.set_retented_data(node_id,
                                              'publiciface',
                                              pubi)
                privi = PrivateIfaceFormset(request.POST,
                                            prefix = "node_%s_privi" % node_id)
                node_widget.set_retented_data(node_id,
                                              'privateiface',
                                              privi)
                
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
                child_ii = []
                child_privi = []
                child_pubi = []
                child_cpu = None
                child_storage = None
                child_memory = None
                if ii.is_valid():
                    child_ii = ii.save(commit = False)
                if pubi.is_valid():
                    child_pubi = pubi.save(commit = False)
                if privi.is_valid():
                    child_privi = privi.save(commit = False)
                if cpu.is_valid():
                    child_cpu = cpu.save(commit = False)
                if storage.is_valid():
                    child_storage = storage.save(commit = False)
                if memory.is_valid():
                    child_memory = memory.save(commit = False)
                node_info[node_id] = {'ii': child_ii,
                                      'pubi': child_pubi,
                                      'privi': child_privi,
                                      'cpu': child_cpu,
                                      'storage': child_storage,
                                      'memory': child_memory}
                
            if api.create_slice({
                'nodes': node_info,
                'user': request.user,
                'name': c_data.get('name'),
                'template': c_data.get('template', None),
                'vlan_nr': c_data.get('vlan_nr', 0),
                'exp_data_uri': c_data.get('exp_data_uri', ''),
                'exp_data_sha256': c_data.get('exp_data_sha256', ''),
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
def allocate_slivers(request, node_id):
    """
    Allocate all slivers from a given node
    """
    keys = api.allocate_slivers({'node_id': node_id})
    messages.info(request, "Allocate sliver task started")
    return HttpResponseRedirect("/node_index/")

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

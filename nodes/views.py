# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from xml.etree import ElementTree
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt

from nodes import settings
from nodes import models as node_models
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
    """
    pass

def get_node_configuration(request):
    """
    Retrieve the node configuration file
    """
    pass

def get_node_public_keys(request):
    """
    Retrieve public keys of node users
    """
    pass

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
    nodes = node_models.Node.objects.all()
    return render_to_response("public/create_slice.html",
                              RequestContext(request,
                                             {
                                                 'nodes': nodes
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

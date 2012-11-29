from __future__ import absolute_import

from django.http import Http404
from rest_framework import generics

from api import api

from .models import Node, Server
from .serializers import ServerSerializer, NodeSerializer


class NodeList(generics.ListCreateAPIView):
    """ 
    **Media type:** [`application/vnd.confine.server.Node.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#node_at_server)
    
    This resource lists the [nodes](http://wiki.confine-project.eu/arch:rest-
    api?&#node_at_server) available in the testbed and provides API URIs to 
    navigate to them.
    """
    model = Node
    serializer_class = NodeSerializer
    filter_fields = ('arch', 'set_state', 'group', 'group__name')


class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Node.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#node_at_server)
    
    This resource describes a node in the testbed as well as listing the 
    [slivers](http://wiki.confine-project.eu/arch:rest-api?&#sliver_at_server)
    intended to run on it with API URIs to navigate to them.
    """
    model = Node
    serializer_class = NodeSerializer


class ServerDetail(generics.RetrieveUpdateDestroyAPIView):
    """ 
    **Media type:** [`application/vnd.confine.server.Server.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#server_at_server)
    
    This resource describes the testbed server (controller).
    """
    model = Server
    serializer_class = ServerSerializer
    
    def get_object(self):
        try:
            return Server.objects.get()
        except Server.DoesNotExist:
            raise Http404


api.register(NodeList, NodeDetail)
api.register(ServerDetail, ServerDetail)

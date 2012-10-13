from controller import api
from django.http import Http404
from nodes.models import Node, Server
from nodes.serializers import ServerSerializer, NodeSerializer
from rest_framework import generics

# TODO refactor this with a ModelResource when they are stable 

class NodeList(generics.ListCreateAPIView):
    """
        List of the nodes available in the testbed.
    """

    model = Node
    serializer_class = NodeSerializer


class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    """ 
        A Node resource describes a node in the testbed (including its associated 
        research device or RD), as well as listing the slivers intended to run 
        on it with API URIs to navigate to them.
    """

    model = Node
    serializer_class = NodeSerializer


class ServerDetail(generics.RetrieveUpdateDestroyAPIView):
    """ This resource describes the testbed server (controller)."""
    model = Server
    serializer_class = ServerSerializer
    
    def get_object(self):
        try:
            return Server.objects.get()
        except Server.DoesNotExist:
            raise Http404


api.register((NodeList, NodeDetail))
api.register((ServerDetail, ServerDetail))

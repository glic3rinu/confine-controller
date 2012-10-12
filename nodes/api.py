from controller import api
from nodes.models import Node
from nodes.serializers import NodeSerializer
from rest_framework import generics

# TODO refactor this with a ModelResource when they are stable 

class Nodes(generics.ListCreateAPIView):
    """
        List of the nodes available in the testbed.
    """

    model = Node
    serializer_class = NodeSerializer


class Node(generics.RetrieveUpdateDestroyAPIView):
    """ 
        A Node resource describes a node in the testbed (including its associated 
        research device or RD), as well as listing the slivers intended to run 
        on it with API URIs to navigate to them.
    """

    model = Node
    serializer_class = NodeSerializer


api.register((Nodes, Node), 'node')

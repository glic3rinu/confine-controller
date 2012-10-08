from nodes.models import Node
from nodes.serializers import NodeSerializer
from rest_framework import generics


class NodeRoot(generics.ListCreateAPIView):
    model = Node
    serializer_class = NodeSerializer


class NodeInstance(generics.RetrieveUpdateDestroyAPIView):
    model = Node
    serializer_class = NodeSerializer



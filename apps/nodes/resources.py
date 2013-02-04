from rest_framework.resources import ModelResource
from nodes.serializers import NodeSerializer
from nodes.models import Node

class NodeResource(ModelResource):
    serializer_class = NodeSerializer
    model = Node



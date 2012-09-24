from models import Node
from rest_framework.serializers import ModelSerializer
from rest_framework.resources import ModelResource


class NodeSerializer(ModelSerializer):
    class Meta:
        model = Node


class NoseResource(ModelResource):
    serializer_class = NodeSerializer
    model = Node

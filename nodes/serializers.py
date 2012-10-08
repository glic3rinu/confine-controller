from rest_framework import serializers
from nodes.models import Node


class NodeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Node


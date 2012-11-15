from rest_framework import serializers

from .models import Server, Node


class ServerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    properties = serializers.Field()
    slivers = serializers.ManyHyperlinkedRelatedField(view_name='sliver-detail',
        read_only=True)
    direct_ifaces = serializers.Field()
    
    class Meta:
        model = Node


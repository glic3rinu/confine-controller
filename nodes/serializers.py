from rest_framework import serializers

from common.serializers import UriHyperlinkedModelSerializer

from .models import Server, Node


class ServerSerializer(UriHyperlinkedModelSerializer):
    class Meta:
        model = Server


class NodeSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    properties = serializers.Field()
    slivers = serializers.ManyHyperlinkedRelatedField(view_name='sliver-detail',
        read_only=True)
    direct_ifaces = serializers.Field()
    
    class Meta:
        model = Node

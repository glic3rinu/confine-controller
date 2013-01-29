from __future__ import absolute_import

from rest_framework import serializers

from api.serializers import UriHyperlinkedModelSerializer, PropertyField

from .models import Server, Node


class ServerSerializer(UriHyperlinkedModelSerializer):
    class Meta:
        model = Server


class NodeSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    # TODO read_only = False
    properties = PropertyField(source='nodeprop_set', required=False, read_only=True)
    slivers = serializers.ManyHyperlinkedRelatedField(view_name='sliver-detail',
        read_only=True)
    direct_ifaces = serializers.Field()
    
    class Meta:
        model = Node

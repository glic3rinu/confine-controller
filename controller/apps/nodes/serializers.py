from __future__ import absolute_import

from rest_framework import serializers

from api.serializers import UriHyperlinkedModelSerializer, PropertyField

from .models import Server, Node, DirectIface


class ServerSerializer(UriHyperlinkedModelSerializer):
    class Meta:
        model = Server


class DirectIface(serializers.ModelSerializer):
    class Meta:
        model = DirectIface


class NodeSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    # TODO read_only = False
    properties = PropertyField(required=False, read_only=True)
    slivers = serializers.ManyHyperlinkedRelatedField(view_name='sliver-detail',
        read_only=True)
    direct_ifaces = DirectIface()
    cert = serializers.Field()
    
    class Meta:
        model = Node

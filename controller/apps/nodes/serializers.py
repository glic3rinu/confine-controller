from __future__ import absolute_import

from rest_framework import serializers

from api.serializers import UriHyperlinkedModelSerializer, PropertyField, RelHyperlinkedRelatedField

from .models import Server, Node, DirectIface


class ServerSerializer(UriHyperlinkedModelSerializer):
    class Meta:
        model = Server


class DirectIface(serializers.ModelSerializer):
    class Meta:
        model = DirectIface


class NodeSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    properties = PropertyField(required=False)
    slivers = RelHyperlinkedRelatedField(many=True, view_name='sliver-detail')
    direct_ifaces = DirectIface()
    cert = serializers.Field()
    boot_sn = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Node

from __future__ import absolute_import

from rest_framework import serializers

from api.serializers import UriHyperlinkedModelSerializer, PropertyField, RelHyperlinkedRelatedField

from .models import Server, Node, DirectIface


class ServerSerializer(UriHyperlinkedModelSerializer):
    class Meta:
        model = Server


class DirectIfaceField(serializers.WritableField):
    def to_native(self, value):
        return [ iface.name for iface in value.all() ]


class NodeSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    properties = PropertyField(required=False)
    slivers = RelHyperlinkedRelatedField(many=True, view_name='sliver-detail')
    direct_ifaces = DirectIfaceField()
    cert = serializers.Field()
    boot_sn = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Node

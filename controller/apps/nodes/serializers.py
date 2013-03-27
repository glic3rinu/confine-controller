from __future__ import absolute_import

from api import serializers

from .models import Server, Node, DirectIface


class ServerSerializer(serializers.UriHyperlinkedModelSerializer):
    class Meta:
        model = Server


class DirectIfaceField(serializers.WritableField):
    def to_native(self, value):
        return [ iface.name for iface in value.all() ]


class NodeSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    properties = serializers.PropertyField(required=False)
    slivers = serializers.RelHyperlinkedRelatedField(many=True, read_only=True,
        view_name='sliver-detail')
    direct_ifaces = DirectIfaceField(required=False)
    cert = serializers.Field()
    boot_sn = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Node

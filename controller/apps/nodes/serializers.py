from __future__ import absolute_import

import json
import six

from api import serializers, exceptions

from .models import Server, Node, DirectIface


class ServerSerializer(serializers.UriHyperlinkedModelSerializer):
    class Meta:
        model = Server


class DirectIfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectIface
        fields = ('name',)
    
    def to_native(self, value):
        return value.name
    
    def field_from_native(self, data, files, field_name, into):
        ifaces = data.get(field_name, [])
        if ifaces:
            data[field_name] = [{'name': iface_name} for iface_name in ifaces]
        return super(DirectIfaceSerializer, self).field_from_native(data, files, field_name, into)
    
    def get_identity(self, data):
        try:
            return data.get('name', None)
        except AttributeError:
            return data


class NodeSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    properties = serializers.PropertyField(required=False)
    slivers = serializers.RelHyperlinkedRelatedField(many=True, read_only=True,
        view_name='sliver-detail')
    direct_ifaces = DirectIfaceSerializer(required=False, many=True, allow_add_remove=True)
    cert = serializers.Field()
    boot_sn = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Node

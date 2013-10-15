from __future__ import absolute_import

import json
import six

from api import serializers, exceptions

from .models import Server, Node, DirectIface


class ServerSerializer(serializers.UriHyperlinkedModelSerializer):
    class Meta:
        model = Server


class DirectIfaceField(serializers.WritableField):
    def to_native(self, value):
        return value.all().values_list('name', flat=True)
    
    def from_native(self, value):
        if value:
            parent = self.parent
            model = getattr(parent.opts.model, self.source or 'direct_ifaces').related.model
            if isinstance(value, six.text_type):
                try:
                    value = json.loads(value)
                except:
                    raise exceptions.ParseError("Malformed iaface: %s" % str(value))
            related_manager = getattr(parent.object, self.source or 'direct_ifaces', False)
            if not related_manager:
                # POST (new parent object)
                return [ model(name=iface) for iface in value ]
            # PUT
            current_ifaces = related_manager.all().values_list('name', flat=True)
            to_delete = set(current_ifaces)-set(value)
            to_create = set(value)-set(current_ifaces)
            # TODO 
#            for iface in to_delete:
#                related_manager.filter(name=iface).delete()
            return [ model(name=iface) for iface in to_create ]
        return []


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

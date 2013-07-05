from __future__ import absolute_import

from api import api, serializers
from nodes.models import Server, Node

from .models import (Island, TincAddress, TincHost, TincClient, TincServer,
    Gateway, Host)


class TincHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TincHost


class IslandSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Island


class TincAddressSerializer(serializers.ModelSerializer):
    island = serializers.RelHyperlinkedRelatedField(view_name='island-detail')
    
    class Meta:
        model = TincAddress
        exclude = ('id', 'server')


class TincClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    island = serializers.RelHyperlinkedRelatedField(view_name='island-detail', required=False)
    
    class Meta:
        model = TincClient
        exclude = ('object_id', 'content_type', 'id')


class TincServerSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    addresses = TincAddressSerializer()
    
    class Meta:
        model = TincServer
        exclude = ('object_id', 'content_type', 'id')


class MgmtNetConfSerializer(serializers.Serializer):
    addr = serializers.Field()
    backend = serializers.CharField(source='name')
    tinc_client = TincClientSerializer()
    tinc_server = TincServerSerializer()
    native = serializers.Field()


class GatewaySerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    mgmt_net = MgmtNetConfSerializer()
    
    class Meta:
        model = Gateway


class HostSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    mgmt_net = MgmtNetConfSerializer()
    
    class Meta:
        model = Host


api.aggregate(Server, MgmtNetConfSerializer, name='mgmt_net')
api.aggregate(Node, MgmtNetConfSerializer, name='mgmt_net')

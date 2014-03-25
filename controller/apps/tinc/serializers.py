from __future__ import absolute_import

from api import api, serializers
from nodes.models import Server, Node
from mgmtnetworks.serializers import MgmtNetConfSerializer

from .models import TincAddress, TincHost, Gateway, Host


class TincAddressSerializer(serializers.ModelSerializer):
    island = serializers.RelHyperlinkedRelatedField(view_name='island-detail')
    
    class Meta:
        model = TincAddress
        exclude = ('id', 'host')


class TincHostSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    pubkey = serializers.CharField(required=True)
    addresses = TincAddressSerializer()

    class Meta:
        model = TincHost
        exclude = ('object_id', 'content_type', 'id')


class GatewaySerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    mgmt_net = MgmtNetConfSerializer()
    tinc = TincHostSerializer()
    
    class Meta:
        model = Gateway


class HostSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    mgmt_net = MgmtNetConfSerializer()
    tinc = TincHostSerializer()
    
    class Meta:
        model = Host


# Aggregate tinc to the Server and Node API
api.aggregate(Server, TincHostSerializer, name='tinc')
api.aggregate(Node, TincHostSerializer, name='tinc')

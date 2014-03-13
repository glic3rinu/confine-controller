from __future__ import absolute_import

from api import api, serializers
from nodes.models import Server, Node

from .models import (TincAddress, TincHost, TincClient, TincServer,
    Gateway, Host)


class TincHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TincHost


class TincAddressSerializer(serializers.ModelSerializer):
    island = serializers.RelHyperlinkedRelatedField(view_name='island-detail')
    
    class Meta:
        model = TincAddress
        exclude = ('id', 'server')


class TincClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    pubkey = serializers.CharField(required=True)
    
    class Meta:
        model = TincClient
        fields = ('name', 'pubkey')


class TincServerSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    addresses = TincAddressSerializer()
    
    class Meta:
        model = TincServer
        exclude = ('object_id', 'content_type', 'id')


class MgmtNetConfSerializer(serializers.Serializer):
    addr = serializers.Field()
    backend = serializers.CharField(source='name', read_only=True)
    tinc_client = TincClientSerializer(required=False)
    tinc_server = TincServerSerializer(required=False)
    native = serializers.BooleanField(required=False)


class GatewaySerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    mgmt_net = MgmtNetConfSerializer()
    
    class Meta:
        model = Gateway


class HostSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    mgmt_net = MgmtNetConfSerializer(read_only=True)
    
    class Meta:
        model = Host


api.aggregate(Server, MgmtNetConfSerializer, name='mgmt_net', read_only=True)
api.aggregate(Node, MgmtNetConfSerializer, name='mgmt_net', read_only=True)

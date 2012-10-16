from common.api import api
from nodes.models import Server, Node
from rest_framework import serializers
from tinc.models import Island, TincAddress, TincHost, TincClient, Host


class TincHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TincHost


class TincAddressSerializer(serializers.ModelSerializer):
    pubkey = serializers.CharField()
    
    class Meta:
        model = TincAddress
        exclude = ('id',)


class IslandSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Island


class TincClientSerializer(serializers.ModelSerializer):
    connect_to = TincAddressSerializer()
    island = IslandSerializer()
    name = serializers.CharField()
    
    class Meta:
        model = TincClient
        exclude = ('object_id', 'content_type', 'id')


class HostSerializer(serializers.HyperlinkedModelSerializer):
    tinc = TincClientSerializer()
    
    class Meta:
        model = Host


api.aggregate(Server, TincClientSerializer, name='tinc')
api.aggregate(Node, TincClientSerializer, name='tinc')

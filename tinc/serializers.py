from apis import rest
from nodes.models import Server
from nodes.serializers import ServerSerializer, ResearchDeviceSerializer
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


rest.api.aggregate(Server, TincClientSerializer, name='tinc')
# TODO hook it to a nested research device or wait until there is no more nesting
#api.aggregate(Node, TincClientSerializer, name='tinc')

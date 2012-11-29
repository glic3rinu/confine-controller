from __future__ import absolute_import

from rest_framework import serializers

from api import api
from api.serializers import UriHyperlinkedModelSerializer
from nodes.models import Server, Node

from .models import (Island, TincAddress, TincHost, TincClient, TincServer, 
    Gateway, Host)


class TincHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TincHost


class TincConnectToSerializer(serializers.ModelSerializer):
    pubkey = serializers.CharField()
    name = serializers.CharField()
    
    class Meta:
        model = TincAddress
        exclude = ('id', 'server', 'island')


class IslandSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Island


class TincAddressSerializer(serializers.ModelSerializer):
    island = IslandSerializer()
    
    class Meta:
        model = TincAddress
        exclude = ('id', 'server')


class TincClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    connect_to = TincConnectToSerializer()
    island = IslandSerializer()
    
    class Meta:
        model = TincClient
        exclude = ('object_id', 'content_type', 'id')


class TincServerSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    connect_to = TincConnectToSerializer()
    addresses = TincAddressSerializer()
    
    class Meta:
        model = TincServer
        exclude = ('object_id', 'content_type', 'id')


class GatewaySerializer(UriHyperlinkedModelSerializer):
    tinc = TincServerSerializer()
    id = serializers.Field()
    
    class Meta:
        model = Gateway


class HostSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    tinc = TincClientSerializer()
    
    class Meta:
        model = Host


api.aggregate(Server, TincServerSerializer, name='tinc')
api.aggregate(Node, TincClientSerializer, name='tinc')

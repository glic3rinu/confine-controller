from rest_framework import serializers
from nodes.models import Server, Node, ResearchDevice
from tinc.serializers import TincHostSerializer, TincClientSerializer

# TODO dynamically hook tinc serializers instead of hardcoding them

class ServerSerializer(serializers.HyperlinkedModelSerializer):
    tinc = TincClientSerializer()

    class Meta:
        model = Server


class ResearchDeviceSerializer(serializers.ModelSerializer):
    tinc = TincClientSerializer()

    class Meta:
        model = ResearchDevice
        exclude = ('node',)


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    researchdevice = ResearchDeviceSerializer()
    
    class Meta:
        model = Node

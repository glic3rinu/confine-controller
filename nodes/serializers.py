from rest_framework import serializers
from nodes.models import Server, Node, ResearchDevice

# TODO dynamically hook other app serializers instead of hardcoding them
#from tinc.serializers import TincHostSerializer, TincClientSerializer


class ServerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server

class ResearchDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResearchDevice
        exclude = ('node',)


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    researchdevice = ResearchDeviceSerializer()
    properties = serializers.Field()
    slivers = serializers.ManyHyperlinkedRelatedField(view_name='sliver-detail')

    class Meta:
        model = Node


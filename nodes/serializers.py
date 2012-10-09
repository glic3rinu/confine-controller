from rest_framework import serializers
from nodes.models import Node, ResearchDevice
from tinc.serializers import TincHostSerializer, TincClientSerializer

#TODO dynamically hook tinc serializers instead of hardcoding them

class ResearchDeviceSerializer(serializers.ModelSerializer):
    tinchost = TincHostSerializer
    tincclient = TincClientSerializer

    class Meta:
        model = ResearchDevice


class NodeSerializer(serializers.HyperlinkedModelSerializer):
    researchdevice = ResearchDeviceSerializer()
    
    class Meta:
        model = Node



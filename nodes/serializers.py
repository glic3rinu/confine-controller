from rest_framework import serializers
from nodes.models import Node, ResearchDevice


class ResearchDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchDevice


class NodeSerializer(serializers.ModelSerializer):
    admin = serializers.HyperlinkedRelatedField(view_name='user_instance')
    researchdevice = ResearchDeviceSerializer()
    
    class Meta:
        model = Node





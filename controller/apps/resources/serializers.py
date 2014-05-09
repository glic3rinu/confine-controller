from __future__ import absolute_import

from api import api, serializers
from controller.models import Testbed
from controller.api import TestbedSerializer
from nodes.models import Node

from . import ResourcePlugin
from .models import Resource, ResourceReq


class ResourceSerializer(serializers.ModelSerializer):
    avail = serializers.Field()
    unit = serializers.CharField(read_only=True)
    
    class Meta:
        model = Resource
        fields = ['name', 'max_req', 'dflt_req', 'unit', 'avail']


class ResourceReqSerializer(serializers.ModelSerializer):
    unit = serializers.CharField(read_only=True)
    
    class Meta:
        model = ResourceReq
        fields = ['name', 'req', 'unit']


for producer_model in ResourcePlugin.get_producers_models():
    if producer_model == Testbed:
        TestbedSerializer.base_fields.update({'testbed_resources':
            ResourceSerializer(source='resources', many=True, required=False)})
        continue
    api.aggregate(producer_model, ResourceSerializer, name='resources', many=True, required=False)


for consumer_model in ResourcePlugin.get_consumers_models():
    api.aggregate(consumer_model, ResourceReqSerializer, name='resources', many=True, required=False)

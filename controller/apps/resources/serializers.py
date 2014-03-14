from __future__ import absolute_import

from api import api, serializers
from nodes.models import Node

from . import ResourcePlugin
from .models import Resource, ResourceReq


class ResourceSerializer(serializers.ModelSerializer):
    unit = serializers.CharField(read_only=True)
    
    class Meta:
        model = Resource
        fields = ['name', 'max_sliver', 'dflt_sliver', 'unit']


# TODO rename name to res_name
class ResourceReqSerializer(serializers.ModelSerializer):
    unit = serializers.CharField(read_only=True)
    
    class Meta:
        model = ResourceReq
        fields = ['name', 'req', 'unit']


for producer_model in ResourcePlugin.get_producers_models():
    api.aggregate(producer_model, ResourceSerializer, name='resources', required=False)


for consumer_model in ResourcePlugin.get_consumers_models():
    api.aggregate(consumer_model, ResourceReqSerializer, name='resources', required=False)

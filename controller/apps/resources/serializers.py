from __future__ import absolute_import

from api import api, serializers
from controller.models import Testbed
from controller.api import TestbedSerializer
from slices.models import Slice

from . import ResourcePlugin
from .models import Resource, ResourceReq
from .resources import VlanRes


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


# Hack to show explicit handled resource (Vlan) - #46-note87
class VlanResourceReqSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_vlan_name')
    unit = serializers.SerializerMethodField('get_vlan_unit')
    req = serializers.SerializerMethodField('get_vlan_req')
    alloc = serializers.SerializerMethodField('get_vlan_alloc')
    
    class Meta:
        model = Slice
        fields = ['name', 'req', 'unit', 'alloc']
    
    def get_vlan_name(self, obj):
        return VlanRes.name
    
    def get_vlan_req(self, obj):
        return int(obj.allow_isolated)
    
    def get_vlan_unit(self, obj):
        return VlanRes.unit
    
    def get_vlan_alloc(self, obj):
        if obj.set_state == Slice.REGISTER:
            return None
        if obj.allow_isolated:
            return 1
        return 0
    
    def to_native(self, value):
        # hack to show as a list of resources
        value = super(VlanResourceReqSerializer, self).to_native(value)
        return [value]


# FIXME wont work until api.aggregate supports nested serializers
#api.aggregate(Slice, VlanResourceReqSerializer, source='*', name='resources', required=False)

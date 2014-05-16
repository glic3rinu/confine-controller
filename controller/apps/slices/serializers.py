from __future__ import absolute_import

import json
import six

from rest_framework.compat import smart_text

from api import serializers
from nodes.settings import NODES_NODE_ARCHS

from .models import Slice, Sliver, Template, SliverIface


class FakeFileField(serializers.CharField):
    """ workaround for displaying related files in a file_uri field """
    def __init__(self, *args, **kwargs):
        self.field_name = kwargs.pop('field')
        super(FakeFileField, self).__init__(*args, **kwargs)
    
#   TODO remove file object._delete
#    def from_native(self, value):
    def to_native(self, value):
        object_file = getattr(self.parent.__object__, self.field_name)
        if object_file:
            request = self.context.get('request', None)
            format = self.context.get('format', None)
            return request.build_absolute_uri(object_file.url)
        return value


class SliverIfaceSerializer(serializers.ModelSerializer):
    parent_name = serializers.Field(source='parent')
    
    class Meta:
        model = SliverIface
        fields = ('nr', 'name', 'type', 'parent_name')
        read_only_fields = ('nr',)
    
    def get_identity(self, data):
        try:
            return data.get('nr', None)
        except AttributeError:
            return data


class SliverSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field(source='api_id')
    interfaces = SliverIfaceSerializer(required=False, many=True, allow_add_remove=True)
    properties = serializers.PropertyField()
    exp_data_uri = FakeFileField(field='exp_data', required=False)
    overlay_uri = FakeFileField(field='overlay', required=False)
    instance_sn = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Sliver
        exclude = ('exp_data', 'overlay')
    
    def to_native(self, obj):
        """ hack for implementing dynamic file_uri's on FakeFile """
        self.__object__ = obj
        return super(SliverSerializer, self).to_native(obj)
    
    def validate(self, attrs):
        """ workaround about nested serialization
            sliverifaces need to be validated with an associated sliver
        """
        super(SliverSerializer, self).validate(attrs)
        ifaces = attrs.get('interfaces', []) or []
        for iface in ifaces:
            Sliver.get_registered_ifaces()[iface.type].clean_model(iface)
        return attrs

    def validate_interfaces(self, attrs, source):
        """ Check if first interface is of type private """
        interfaces = attrs.get(source, [])
        if 'private' not in [iface.type for iface in interfaces]:
           raise serializers.ValidationError('At least one private interface is required.')
        return attrs


class SliverDetailSerializer(SliverSerializer):
    class Meta:
        model = Sliver
        read_only_fields = ('node', 'slice')


class SliceCreateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    expires_on = serializers.DateTimeField(read_only=True)
    instance_sn = serializers.IntegerField(read_only=True)
    new_sliver_instance_sn = serializers.IntegerField(read_only=True)
    vlan_nr = serializers.IntegerField(read_only=True)
    properties = serializers.PropertyField()
    exp_data_uri = FakeFileField(field='exp_data', required=False)
    overlay_uri = FakeFileField(field='overlay', required=False)
    slivers = serializers.RelHyperlinkedRelatedField(many=True, read_only=True,
        view_name='sliver-detail')
    
    class Meta:
        model = Slice
        exclude = ('set_state', 'exp_data', 'overlay')
    
    def to_native(self, obj):
        """ hack for implementing dynamic file_uri's on FakeFile """
        self.__object__ = obj
        return super(SliceCreateSerializer, self).to_native(obj)


class SliceSerializer(SliceCreateSerializer):
    class Meta:
        model = Slice
        exclude = ('exp_data', 'overlay')
        read_only_fields = ('group',)


class TemplateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    image_uri = FakeFileField(field='image')
    node_archs = serializers.MultiSelectField(choices=NODES_NODE_ARCHS)
    is_active = serializers.BooleanField()
    
    class Meta:
        model = Template
        exclude = ['image']
    
    def to_native(self, obj):
        """ hack for implementing dynamic file_uri's on FakeFile """
        self.__object__ = obj
        return super(TemplateSerializer, self).to_native(obj)


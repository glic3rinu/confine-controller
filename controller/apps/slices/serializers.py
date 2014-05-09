from __future__ import absolute_import

import json
import six

from controller.utils.apps import is_installed
from rest_framework.compat import smart_text

from api import serializers, exceptions
from api.validators import validate_properties
from nodes.settings import NODES_NODE_ARCHS

from .models import Slice, Sliver, SliverDefaults, SliverIface, Template


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


class FileURLField(serializers.CharField):
    """ Readonly Absolute URL field used for backwards compatibility """
    def __init__(self, *args, **kwargs):
        kwargs.update({'read_only': True})
        super(FileURLField, self).__init__(*args, **kwargs)
    def to_native(self, value):
        if value:
            request = self.context.get('request', None)
            return request.build_absolute_uri(value)
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
    properties = serializers.PropertyField(default={})
    data_uri = FakeFileField(field='data', required=False)
    overlay_uri = FakeFileField(field='overlay', required=False)
    instance_sn = serializers.IntegerField(read_only=True)
    
    # backwards compatibility (readonly)
    exp_data_uri = FileURLField(source='data_uri')
    exp_data_sha256 = serializers.Field(source='data_sha256')
    
    class Meta:
        model = Sliver
        exclude = ('data', 'overlay')
    
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
           raise exceptions.ParseError(detail='At least one private interface is required.')
        return attrs

    def validate_properties(self, attrs, source):
        return validate_properties(self, attrs, source)


class SliverDetailSerializer(SliverSerializer):
    class Meta:
        model = Sliver
        read_only_fields = ('node', 'slice')
        exclude = ('data', 'overlay')


class SliverDefaultsSerializer(serializers.ModelSerializer):
    instance_sn = serializers.IntegerField(read_only=True)
    data_uri = FakeFileField(field='data', required=False)
    overlay_uri = FakeFileField(field='overlay', required=False)
    template = serializers.RelHyperlinkedRelatedField(view_name='template-detail')
    # FIXME refactor move to resources app when api.aggregate supports nested serializers
    if is_installed('resources'):
        from resources.serializers import ResourceReqSerializer
        resources = ResourceReqSerializer(source='slice_resources', many=True, required=False)

    class Meta:
        model = SliverDefaults
        exclude = ('id', 'slice', 'data', 'overlay')
    
    def to_native(self, obj):
        """ hack for implementing dynamic file_uri's on FakeFile """
        self.__object__ = obj
        return super(SliverDefaultsSerializer, self).to_native(obj)


class SliceCreateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    expires_on = serializers.DateTimeField(read_only=True)
    instance_sn = serializers.IntegerField(read_only=True)
    properties = serializers.PropertyField(default={})
    isolated_vlan_tag = serializers.IntegerField(read_only=True)
    sliver_defaults = SliverDefaultsSerializer()
    slivers = serializers.RelHyperlinkedRelatedField(many=True, read_only=True,
        view_name='sliver-detail')
    
    # backwards compatibility (readonly)
    new_sliver_instance_sn = serializers.Field(source='sliver_defaults.instance_sn')
    exp_data_uri = FileURLField(source='sliver_defaults.data_uri')
    exp_data_sha256 = serializers.Field(source='sliver_defaults.data_sha256')
    overlay_uri = FileURLField(source='sliver_defaults.overlay_uri')
    overlay_sha256 = serializers.Field(source='sliver_defaults.overlay_sha256')
    template = serializers.RelHyperlinkedRelatedField(source='sliver_defaults.template',
        read_only=True, view_name='template-detail')
    vlan_nr = serializers.Field()
    
    class Meta:
        model = Slice
        exclude = ('set_state',)

    def validate_properties(self, attrs, source):
        return validate_properties(self, attrs, source)


class SliceSerializer(SliceCreateSerializer):
    class Meta:
        model = Slice
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


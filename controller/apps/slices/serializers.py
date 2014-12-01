from __future__ import absolute_import

from controller.utils.apps import is_installed
from urlparse import urlparse

from api import serializers
from nodes.settings import NODES_NODE_ARCHS

from .models import Slice, Sliver, SliverDefaults, SliverIface, Template


class FakeFileField(serializers.CharField):
    """ workaround for displaying related files in a file_uri field """
    def __init__(self, *args, **kwargs):
        self.field_name = kwargs.pop('field')
        super(FakeFileField, self).__init__(*args, **kwargs)
    
    def from_native(self, value):
        request = self.context.get('request', None)
        if request and value:
            request_host = request.get_host().split(':')[0]
            file_url = urlparse(value)
            # check if file_uri matchs with file stored in controller (#494)
            if request_host == file_url.hostname:
                return file_url.path
        return super(FakeFileField, self).from_native(value)
    
    def to_native(self, value):
        object_file = getattr(self.parent.__object__, self.field_name)
        if object_file:
            request = self.context.get('request', None)
            return request.build_absolute_uri(object_file.url)
        return value


class FileURLField(serializers.CharField):
    """ Readonly Absolute URL field used for backwards compatibility """
    def __init__(self, *args, **kwargs):
        self.field_name = kwargs.pop('field', '')
        kwargs.update({'read_only': True})
        super(FileURLField, self).__init__(*args, **kwargs)
    
    def to_native(self, value):
        """
        Build an absolute URI based on the File URL if any,
        otherwise fallback on field_name_uri
        """
        fieldfile = getattr(value, self.field_name)
        if fieldfile:
            uri = getattr(fieldfile, 'url')
            request = self.context.get('request')
            return request.build_absolute_uri(uri)
        return getattr(value, self.field_name + '_uri')


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
    data_uri = FakeFileField(field='data', required=False)
    instance_sn = serializers.IntegerField(read_only=True)
    mgmt_net = serializers.Field()
    
    # FIXME remove when api.aggregate supports nested serializers
    # is only required because SliverDefaultsSerializer imports resources
    # serializers, and breaks api.aggregate functionality based on
    # api._registry (see class SliverDefaultsSerializer)
    if is_installed('resources'):
        from resources.serializers import ResourceReqSerializer
        resources = ResourceReqSerializer(many=True, required=False)
    
    # backwards compatibility (readonly)
    exp_data_uri = FileURLField(source='*', field='data')
    exp_data_sha256 = serializers.Field(source='data_sha256')
    
    class Meta:
        model = Sliver
        exclude = ('data',)
    
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
        """Check that one interface of type private has been defined."""
        interfaces = attrs.get(source, [])
        priv_ifaces = 0
        for iface in interfaces:
            if iface.type == 'private':
                priv_ifaces += 1
            if priv_ifaces > 1:
                raise serializers.ValidationError('There can only be one interface of type private.')
        if priv_ifaces == 0:
            raise serializers.ValidationError('There must exist one interface of type private.')
        return attrs


class SliverDetailSerializer(SliverSerializer):
    class Meta:
        model = Sliver
        read_only_fields = ('node', 'slice')
        exclude = ('data',)


class SliverDefaultsSerializer(serializers.ModelSerializer):
    instance_sn = serializers.IntegerField(read_only=True)
    data_uri = FakeFileField(field='data', required=False)
    template = serializers.RelHyperlinkedRelatedField(view_name='template-detail')
    # FIXME refactor move to resources app when api.aggregate supports nested serializers
    if is_installed('resources'):
        from resources.serializers import ResourceReqSerializer
        resources = ResourceReqSerializer(source='slice_resources', many=True, required=False)

    class Meta:
        model = SliverDefaults
        exclude = ('id', 'slice', 'data')
    
    def to_native(self, obj):
        """ hack for implementing dynamic file_uri's on FakeFile """
        self.__object__ = obj
        return super(SliverDefaultsSerializer, self).to_native(obj)


class SliceCreateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    expires_on = serializers.DateTimeField(read_only=True)
    instance_sn = serializers.IntegerField(read_only=True)
    properties = serializers.PropertyField()
    isolated_vlan_tag = serializers.IntegerField(read_only=True)
    sliver_defaults = SliverDefaultsSerializer()
    slivers = serializers.RelHyperlinkedRelatedField(many=True, read_only=True,
        view_name='sliver-detail')
    
    # backwards compatibility (readonly)
    new_sliver_instance_sn = serializers.Field(source='sliver_defaults.instance_sn')
    exp_data_uri = FileURLField(source='sliver_defaults', field='data')
    exp_data_sha256 = serializers.Field(source='sliver_defaults.data_sha256')
    template = serializers.RelHyperlinkedRelatedField(source='sliver_defaults.template',
        read_only=True, view_name='template-detail')
    vlan_nr = serializers.Field()
    
    class Meta:
        model = Slice
        exclude = ('set_state',)


class SliceSerializer(SliceCreateSerializer):
    # Hack to show explicit handled resource (Vlan) - #46-note87
    # FIXME: can be removed when monkey-patch works in resources.serializers
    if is_installed('resources'):
        from resources.serializers import VlanResourceReqSerializer
        resources = VlanResourceReqSerializer(source='*', read_only=True, required=False)
    
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


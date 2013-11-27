from __future__ import absolute_import

import json
import six

from rest_framework.compat import smart_text

from api import serializers, exceptions
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
        try:
            has_file = getattr(self.parent.object, self.field_name)
        except AttributeError:
            # List with queryset
            object_id = self.parent.fields['id']
            if hasattr(object_id, '_value'):
                obj = self.parent.object.get(id=object_id._value)
                has_file = getattr(obj, self.field_name)
            has_file = False
        if has_file:
            request = self.context.get('request', None)
            format = self.context.get('format', None)
            return request.build_absolute_uri(value)
        return value


class SliverIfaceSerializer(serializers.ModelSerializer):
    parent_name = serializers.Field(source='parent')
    
    class Meta:
        model = SliverIface
        fields = ('nr', 'name', 'type', 'parent_name')
    
    def get_identity(self, data):
        try:
            return data.get('nr', None)
        except AttributeError:
            return data


class SliverSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    interfaces = SliverIfaceSerializer(required=False, many=True, allow_add_remove=True)
    properties = serializers.PropertyField(required=False)
    exp_data_uri = FakeFileField(field='exp_data', required=False)
    overlay_uri = FakeFileField(field='overlay', required=False)
    instance_sn = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Sliver
        exclude = ('exp_data', 'overlay')
    
    def validate(self, attrs):
        """ workaround about nested serialization
            sliverifaces need to be validated with an associated sliver
        """
        super(SliverSerializer, self).validate(attrs)
        ifaces = attrs.get('interfaces', []) or []
        for iface in ifaces:
            Sliver.get_registered_ifaces()[iface.type].clean_model(iface)
        return attrs


class SliceSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    slivers = serializers.RelHyperlinkedRelatedField(many=True, read_only=True,
        view_name='sliver-detail')
    properties = serializers.PropertyField(required=False)
    exp_data_uri = FakeFileField(field='exp_data', required=False)
    overlay_uri = FakeFileField(field='overlay', required=False)
    instance_sn = serializers.IntegerField(read_only=True)
    new_sliver_instance_sn = serializers.IntegerField(read_only=True)
    expires_on = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Slice
        exclude = ('exp_data', 'overlay')


class TemplateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    image_uri = FakeFileField(field='image')
    node_archs = serializers.MultiSelectField(choices=NODES_NODE_ARCHS)
    
    class Meta:
        model = Template
        exclude = ['image']


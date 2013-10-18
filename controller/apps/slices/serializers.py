from __future__ import absolute_import

import json
import six

from api import serializers, exceptions

from .models import Slice, Sliver, Template, SliverIface


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
    interfaces = SliverIfaceSerializer(required=False, many=True, allow_add_remove=True)
    properties = serializers.PropertyField(required=False)
    exp_data_uri = serializers.HyperlinkedFileField(source='exp_data', required=False,
        read_only=True)
    exp_data_sha256 = serializers.Field()
    overlay_uri = serializers.HyperlinkedFileField(source='overlay', required=False,
        read_only=True)
    overlay_sha256 = serializers.Field()
    instance_sn = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Sliver
        exclude = ('exp_data', 'overlay')


class SliceSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    slivers = serializers.RelHyperlinkedRelatedField(many=True, read_only=True,
        view_name='sliver-detail')
    properties = serializers.PropertyField(required=False)
    exp_data_uri = serializers.HyperlinkedFileField(source='exp_data', required=False,
        read_only=True)
    exp_data_sha256 = serializers.Field()
    overlay_uri = serializers.HyperlinkedFileField(source='overlay', required=False,
        read_only=True)
    overlay_sha256 = serializers.Field()
    instance_sn = serializers.IntegerField(read_only=True)
    new_sliver_instance_sn = serializers.IntegerField(read_only=True)
    expires_on = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Slice
        exclude = ('exp_data', 'overlay')


class TemplateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    image_sha256 = serializers.CharField(read_only=True)
    image_uri = serializers.HyperlinkedFileField(source='image')
    
    class Meta:
        model = Template
        exclude = ['image']


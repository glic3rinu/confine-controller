from __future__ import absolute_import

from rest_framework import serializers

from api.serializers import (UriHyperlinkedModelSerializer, HyperlinkedFileField,
    RelManyHyperlinkedRelatedField)

from .models import Slice, Sliver, Template, SliverIface


class IfaceSerializer(serializers.ModelSerializer):
    parent_name = serializers.Field()
    
    class Meta:
        model = SliverIface
        fields = ['name', 'nr', 'type', 'parent_name']


class SliverSerializer(UriHyperlinkedModelSerializer):
    interfaces = IfaceSerializer()
    properties = serializers.Field()
    exp_data_sha256 = serializers.CharField(read_only=True)
    exp_data_uri = HyperlinkedFileField(source='exp_data')
    
    class Meta:
        model = Sliver
        exclude = ['exp_data']


class SliceSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    slivers = RelManyHyperlinkedRelatedField(view_name='sliver-detail', read_only=True)
    properties = serializers.Field()
    exp_data_sha256 = serializers.CharField(read_only=True)
    exp_data_uri = HyperlinkedFileField(source='exp_data')
    
    class Meta:
        model = Slice
        exclude = ['exp_data']


class TemplateSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    image_sha256 = serializers.CharField(read_only=True)
    image_uri = HyperlinkedFileField(source='image')
    
    class Meta:
        model = Template
        exclude = ['image']


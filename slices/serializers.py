from rest_framework import serializers

from common.serializers import (UriHyperlinkedModelSerializer, HyperlinkedFileField,
    RelManyHyperlinkedRelatedField)

from .models import Slice, Sliver, Template


class IfaceSerializer(serializers.Serializer):
    name = serializers.CharField()
    type = serializers.CharField()
    use_default_gw = serializers.BooleanField()
    parent_name = serializers.CharField()


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


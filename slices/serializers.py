from rest_framework import serializers

from common.serializers import UriHyperlinkedModelSerializer

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
    
    class Meta:
        model = Sliver
        # FIXME bug in rest_framework2 HyperLinkedRelations with null=True blowup
        exclude = ['template']


class SliceSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    slivers = serializers.ManyHyperlinkedRelatedField(view_name='sliver-detail',
        read_only=True)
    properties = serializers.Field()
    exp_data_sha256 = serializers.CharField(read_only=True)
    
    class Meta:
        model = Slice


class TemplateSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    image_sha256 = serializers.CharField(read_only=True)
    
    class Meta:
        model = Template



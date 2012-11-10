from rest_framework import serializers

from slices.models import Slice, Sliver, Template


class IfaceSerializer(serializers.Serializer):
    name = serializers.CharField()
    type = serializers.CharField()
    use_default_gw = serializers.BooleanField()
    parent_name = serializers.CharField()


class SliverSerializer(serializers.HyperlinkedModelSerializer):
    interfaces = IfaceSerializer()
    properties = serializers.Field()
    exp_data_sha256 = serializers.CharField(read_only=True)
    
    class Meta:
        model = Sliver
        # FIXME bug in rest_framework2 HyperLinkedRelations with null=True blowup
        exclude = ['template']


class SliceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    slivers = serializers.ManyHyperlinkedRelatedField(view_name='sliver-detail',
        read_only=True)
    properties = serializers.Field()
    exp_data_sha256 = serializers.CharField(read_only=True)
    
    class Meta:
        model = Slice


class TemplateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    data_sha256 = serializers.CharField(read_only=True)
    
    class Meta:
        model = Template



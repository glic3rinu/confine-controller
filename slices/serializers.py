from rest_framework import serializers
from slices.models import Slice, Sliver, Template

class ProperiesSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super(ProperiesSerializer, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            for prop in instance:
                self.fields[prop.name] = prop.value


class IfaceSerializer(serializers.Serializer):
    name = serializers.CharField()
    type = serializers.CharField()
    use_default_gw = serializers.BooleanField()
    parent_name = serializers.CharField()


class SliverSerializer(serializers.HyperlinkedModelSerializer):
    interfaces = IfaceSerializer()
    properties = serializers.Field()
    
    class Meta:
        model = Sliver


class SliceSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    slivers = serializers.ManyHyperlinkedRelatedField(view_name='sliver-detail')
    properties = serializers.Field()
    
    class Meta:
        model = Slice


class TemplateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Template



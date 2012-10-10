from rest_framework import serializers
from slices.models import Slice, Sliver, Template


class SliceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Slice


class SliverSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sliver


class TemplateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Template



from __future__ import absolute_import

from rest_framework import serializers

from api.serializers import (UriHyperlinkedModelSerializer, HyperlinkedFileField,
    RelManyHyperlinkedRelatedField, PropertyField)

from .models import Slice, Sliver, Template, SliverIface


class IfaceSerializer(serializers.ModelSerializer):
    parent_name = serializers.Field()
    
    class Meta:
        model = SliverIface
        fields = ['name', 'nr', 'type', 'parent_name']


class SliverSerializer(UriHyperlinkedModelSerializer):
    interfaces = IfaceSerializer()
    properties = PropertyField(source='sliverprop_set', required=False)
    exp_data = HyperlinkedFileField(source='exp_data', required=False)
    
    class Meta:
        model = Sliver
    
    def restore_object(self, attrs, instance=None):
        # TODO get rid of this
        """ preliminary hack to make sure sliverprops get saved """
        # Pop from attrs for avoiding AttributeErrors when POSTing
        props = attrs.pop('sliverprop_set', None)
        instance = super(SliverSerializer, self).restore_object(attrs, instance=instance)
        if props is not None:
            # add it to related_data for future saving
            self.related_data['sliverprop_set'] = props
        return instance


class SliceSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    slivers = RelManyHyperlinkedRelatedField(view_name='sliver-detail', read_only=True)
    properties = PropertyField(source='sliverprop_set', required=False)
    exp_data = HyperlinkedFileField(source='exp_data', required=False)
    
    class Meta:
        model = Slice
    
    def restore_object(self, attrs, instance=None):
        # TODO get rid of this
        """ preliminary hack to make sure sliverprops get saved """
        # Pop from attrs for avoiding AttributeErrors when POSTing
        props = attrs.pop('sliceprop_set', None)
        instance = super(SliverSerializer, self).restore_object(attrs, instance=instance)
        if props is not None:
            # add it to related_data for future saving
            self.related_data['sliceprop_set'] = props
        return instance


class TemplateSerializer(UriHyperlinkedModelSerializer):
    id = serializers.Field()
    image_sha256 = serializers.CharField(read_only=True)
    image_uri = HyperlinkedFileField(source='image')
    
    class Meta:
        model = Template
        exclude = ['image']


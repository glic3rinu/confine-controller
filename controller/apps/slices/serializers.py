from __future__ import absolute_import

import ast

from api import serializers

from .models import Slice, Sliver, Template, SliverIface


class IfaceField(serializers.WritableField):
    def to_native(self, value):
        return [ {'nr': iface.nr,
                  'type': iface.type,
                  'name': iface.name,
                  'parent_name': None if not iface.parent else iface.parent.name } for iface in value.all() ]
    
    def from_native(self, value):
        parent = self.parent
        related_manager = getattr(parent.object, self.source or 'interfaces', False)
        ifaces = []
        if value:
            model = getattr(parent.opts.model, self.source or 'interfaces').related.model
            list_ifaces = ast.literal_eval(str(value))
            if not related_manager:
                # POST (new parent object
                return [ model(name=iface['name'], type=iface['type'], parent=iface.get('parent', None)) for iface in list_ifaces ]
            # PUT
            for iface in list_ifaces:
                try:
                    # Update existing ifaces
                    iface = related_manager.get(name=iface['name'])
                except model.DoesNotExist:
                    # Create a new one
                    iface = model(name=iface['name'], type=iface['type'], parent=iface.get('parent', None))
                else:
                    iface.type = iface['type']
                    iface.parent = iface['parent']
                ifaces.append(iface)
        # Discart old values
        if related_manager:
            related_manager.all().delete()
        return ifaces


class SliverSerializer(serializers.UriHyperlinkedModelSerializer):
    interfaces = IfaceField()
    properties = serializers.PropertyField(required=False)
    exp_data = serializers.HyperlinkedFileField(source='exp_data', required=False)
    instance_sn = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Sliver
    
    def restore_object(self, attrs, instance=None):
        # TODO get rid of this
        """ preliminary hack to make sure sliverprops get saved """
        # Pop from attrs for avoiding AttributeErrors when POSTing
        props = attrs.pop('properties', None)
        ifaces = attrs.pop('interfaces', None)
        instance = super(SliverSerializer, self).restore_object(attrs, instance=instance)
        if props is not None:
            # add it to related_data for future saving
            self.related_data['properties'] = props
        if ifaces is not None:
            # TODO do proper clean and validation
            self.related_data['interfaces'] = ifaces
        return instance


class SliceSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    slivers = serializers.RelHyperlinkedRelatedField(many=True, read_only=True, 
        view_name='sliver-detail')
    properties = serializers.PropertyField(required=False)
    exp_data = serializers.HyperlinkedFileField(source='exp_data', required=False)
    instance_sn = serializers.IntegerField(read_only=True)
    new_sliver_instance_sn = serializers.IntegerField(read_only=True)
    expires_on = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Slice
    
    def restore_object(self, attrs, instance=None):
        # TODO get rid of this
        """ preliminary hack to make sure sliverprops get saved """
        # Pop from attrs for avoiding AttributeErrors when POSTing
        props = attrs.pop('properties', None)
        instance = super(SliceSerializer, self).restore_object(attrs, instance=instance)
        if props is not None:
            # add it to related_data for future saving
            self.related_data['properties'] = props
        return instance


class TemplateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    image_sha256 = serializers.CharField(read_only=True)
    image_uri = serializers.HyperlinkedFileField(source='image')
    
    class Meta:
        model = Template
        exclude = ['image']


from __future__ import absolute_import

import ast

from api import serializers, exceptions

from .models import Slice, Sliver, Template, SliverIface


class IfaceField(serializers.WritableField):
    def to_native(self, value):
        return [ {'nr': iface.nr,
                  'type': iface.type,
                  'name': iface.name,
                  'parent_name': getattr(iface.parent, 'name', None) } for iface in value.all() ]
    
    def from_native(self, value):
        parent = self.parent
        node = parent.fields['node'].from_native(parent.init_data['node'])
        
        def get_node_iface(iface):
            """ helper function """
            iface_name = iface.get('parent_name', None)
            if iface_name is not None:
                try:
                    return node.direct_ifaces.get(name=iface_name)
                except node.direct_ifaces.model.DoesNotExist:
                    raise exceptions.UnprocessableEntity('Direct Iface whit name "%s" '
                        'does not exists for this node.' % iface_name)
            return None
        
        related_manager = getattr(parent.object, self.source or 'interfaces', False)
        ifaces = []
        if value:
            model = getattr(parent.opts.model, self.source or 'interfaces').related.model
            try:
                list_ifaces = ast.literal_eval(str(value))
            except SyntaxError as e:
                raise exceptions.ParseError("Malformed Iface: %s" % str(value))
            if not related_manager:
                # POST (new parent object
                return [ model(name=iface['name'],
                               type=iface['type'],
                               parent=get_node_iface(iface)) for iface in list_ifaces ]
            # PUT
            for iface in list_ifaces:
                try:
                    # Update existing ifaces
                    iface = related_manager.get(name=iface['name'])
                except model.DoesNotExist:
                    # Create a new one
                    iface = model(name=iface['name'],
                                  type=iface['type'],
                                  parent=get_node_iface(iface))
                else:
                    iface.type = iface['type']
                    iface.parent = get_node_iface(iface)
                ifaces.append(iface)
        # Discart old values
        if related_manager:
            related_manager.all().delete()
        return ifaces


class SliverSerializer(serializers.UriHyperlinkedModelSerializer):
    interfaces = IfaceField()
    properties = serializers.PropertyField(required=False)
    exp_data_uri = serializers.HyperlinkedFileField(source='exp_data', required=False,
        read_only=True)
    exp_data_sha256 = serializers.Field()
    instance_sn = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Sliver
        exclude = ('exp_data',)


class SliceSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    slivers = serializers.RelHyperlinkedRelatedField(many=True, read_only=True,
        view_name='sliver-detail')
    properties = serializers.PropertyField(required=False)
    exp_data_uri = serializers.HyperlinkedFileField(source='exp_data', required=False,
        read_only=True)
    exp_data_sha256 = serializers.Field()
    instance_sn = serializers.IntegerField(read_only=True)
    new_sliver_instance_sn = serializers.IntegerField(read_only=True)
    expires_on = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Slice
        exclude = ('exp_data',)


class TemplateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    image_sha256 = serializers.CharField(read_only=True)
    image_uri = serializers.HyperlinkedFileField(source='image')
    
    class Meta:
        model = Template
        exclude = ['image']


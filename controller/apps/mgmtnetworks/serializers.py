from __future__ import absolute_import

from api import api, serializers
from nodes.models import Server, Node

from .models import MgmtNetConf


class MgmtNetConfSerializer(serializers.ModelSerializer):
    """ MgmtNetConf readonly serializer used in MgmtNetConfRelatedField """
    addr = serializers.Field()
    backend = serializers.CharField()
    
    class Meta:
        model = MgmtNetConf
        exclude = ('id', 'content_type', 'object_id')


class MgmtNetConfRelatedField(serializers.RelatedField):
    """ MgmtNetConf writable serializer """
    read_only = False
    
    def to_native(self, value):
        """ Convert to serialized fields """
        try:
            # GenericRelation
            mgmt_net = value.first()
        except AttributeError:
            # MgmtNetConf object
            mgmt_net = value
        if mgmt_net is None:
            return {}
        return MgmtNetConfSerializer(mgmt_net).to_native(mgmt_net)
    
    def from_native(self, data):
        """ Return a list of management network objects """
        data = self.validate(data)
        mgmt_net = MgmtNetConf(backend=data.get('backend'))
        mgmt_net.full_clean(exclude=['content_type', 'object_id'])
        return [mgmt_net]

    def validate(self, attrs):
        if 'backend' not in attrs:
            raise serializers.ValidationError('backend field must be provided.')
        return attrs


# Aggregate mgmt_network to the API
for model in [Server, Node]:
    api.aggregate(model, MgmtNetConfRelatedField, name='mgmt_net', source='related_mgmtnet')

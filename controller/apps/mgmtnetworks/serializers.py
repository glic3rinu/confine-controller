from __future__ import absolute_import

from api import api, serializers
from nodes.models import Server, Node

from .models import MgmtNetConf


## backwards compatibility #157 ##
class _TincAddressSerializer(serializers.ModelSerializer):
    island = serializers.RelHyperlinkedRelatedField(view_name='island-detail')
    
    class Meta:
        from tinc.models import TincAddress
        model = TincAddress
        fields = ('island', 'addr', 'port')


class _TincClientSerializer(serializers.ModelSerializer):
    """ backwards compatibility """
    name = serializers.CharField(read_only=True)
    pubkey = serializers.CharField(required=True)
    
    class Meta:
        from tinc.models import TincHost
        model = TincHost
        fields = ('name', 'pubkey')


class _TincServerSerializer(_TincClientSerializer):
    addresses = _TincAddressSerializer()
    is_active = serializers.SerializerMethodField('fake_is_active')
    
    class Meta:
        from tinc.models import TincHost
        model = TincHost
        fields = ('name', 'pubkey', 'addresses', 'is_active')
    
    def fake_is_active(self, obj):
        return True

## end of backwards compatibility #157 ##


class MgmtNetConfSerializer(serializers.ModelSerializer):
    """ MgmtNetConf readonly serializer used in MgmtNetConfRelatedField """
    addr = serializers.Field()
    backend = serializers.CharField()
    
    ## backwards compatibility #157 ##
    tinc_client = _TincClientSerializer(read_only=True)
    tinc_server = _TincServerSerializer(read_only=True)
    native = serializers.Field()
    
    class Meta:
        model = MgmtNetConf
        exclude = ('id', 'content_type', 'object_id')
    
    ## backwards compatibility #157.note-36 ##
    def transform_backend(self, obj, value):
        if value == 'tinc':
            value = 'tinc_client' if obj.tinc_server() is None else 'tinc_server'
        return value


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
        ## backwards compatibility #157.note-36 ##
        ## keep tinc_{client|server} until all nodes are compatible ##
        if attrs['backend'] in ['tinc_client', 'tinc_server']:
            attrs['backend'] = MgmtNetConf.TINC
        return attrs


# Aggregate mgmt_network to the API
for model in [Server, Node]:
    api.aggregate(model, MgmtNetConfRelatedField, name='mgmt_net', source='related_mgmtnet')

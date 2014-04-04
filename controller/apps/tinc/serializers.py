from __future__ import absolute_import

from api import api, serializers
from nodes.models import Server, Node
from mgmtnetworks.serializers import MgmtNetConfRelatedField

from .models import TincAddress, TincHost, Gateway, Host


class TincAddressSerializer(serializers.ModelSerializer):
    island = serializers.RelHyperlinkedRelatedField(view_name='island-detail')
    
    class Meta:
        model = TincAddress
        exclude = ('id', 'host')


class TincHostSerializer(serializers.ModelSerializer):
    """ TincHost readonly serializer """
    name = serializers.CharField(read_only=True)
    pubkey = serializers.CharField(required=True)
    addresses = TincAddressSerializer()

    class Meta:
        model = TincHost
        exclude = ('object_id', 'content_type', 'id')


class TincHostRelatedField(serializers.RelatedField):
    """ TincHost writable serializer """
    default = [] # override default when field no provided
    read_only = False
    
    def to_native(self, value):
        """ Convert to serialized fields """
        try:
            # GenericRelation
            tinc = value.first()
        except AttributeError:
            # TincHost object
            tinc = value
        if tinc is None:
            return {}
        return TincHostSerializer(tinc).to_native(tinc)
    
    def from_native(self, data):
        """ Return a list of tinc configuration objects """
        if data:
            tinc_host = TincHost(pubkey=data.get('pubkey'))
            tinc_host.full_clean(exclude=['content_type', 'object_id'])
            return [tinc_host]
        return []


class GatewaySerializer(serializers.UriHyperlinkedModelSerializer,
                        serializers.MgmtNetComponentModelSerializer):
    id = serializers.Field()
    mgmt_net = MgmtNetConfRelatedField(source='related_mgmtnet')
    tinc = TincHostRelatedField(source='related_tinc', required=False)
    
    class Meta:
        model = Gateway


class HostCreateSerializer(serializers.UriHyperlinkedModelSerializer,
                           serializers.MgmtNetComponentModelSerializer):
    id = serializers.Field()
    mgmt_net = MgmtNetConfRelatedField(source='related_mgmtnet')
    tinc = TincHostRelatedField(source='related_tinc', required=False)
    
    class Meta:
        model = Host
        exclude = ('owner',)


class HostSerializer(HostCreateSerializer):
    class Meta:
        model = Host


# Aggregate tinc to the Server and Node API
api.aggregate(Server, TincHostRelatedField, name='tinc', source='related_tinc', required=False)
api.aggregate(Node, TincHostRelatedField, name='tinc', source='related_tinc', required=False)

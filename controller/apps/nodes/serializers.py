from __future__ import absolute_import

import json
import six

from api import serializers

from . import settings
from .models import DirectIface, Island, Node, Server


class ServerSerializer(serializers.UriHyperlinkedModelSerializer):
    properties = serializers.PropertyField()
    
    class Meta:
        model = Server


class DirectIfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectIface
        fields = ('name',)
    
    def to_native(self, value):
        return value.name
    
    def field_from_native(self, data, files, field_name, into):
        ifaces = data.get(field_name, [])
        if ifaces:
            data[field_name] = [{'name': iface_name} for iface_name in ifaces]
        return super(DirectIfaceSerializer, self).field_from_native(data, files, field_name, into)
    
    def get_identity(self, data):
        try:
            return data.get('name', None)
        except AttributeError:
            return data


class IslandSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Island


#239 Remove firmware configuration cruft from data model
FW_CONFIG_FIELDS = ('local_iface', 'priv_ipv4_prefix', 'sliver_pub_ipv6',
    'sliver_pub_ipv4', 'sliver_pub_ipv4_range', 'sliver_mac_prefix')
class NodeCreateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    properties = serializers.PropertyField()
    arch = serializers.ChoiceField(choices=settings.NODES_NODE_ARCHS, required=True)
    slivers = serializers.RelHyperlinkedRelatedField(many=True, read_only=True,
        view_name='sliver-detail')
    direct_ifaces = DirectIfaceSerializer(required=False, many=True, allow_add_remove=True)
    cert = serializers.Field()
    boot_sn = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Node
        exclude = ('set_state',) + FW_CONFIG_FIELDS

    def get_fields(self, *args, **kwargs):
        """
        Filter groups: the user creating this node must be a
        group or node administrator of this group, and the group
        must have node creation allowed (/allow_nodes=true).
        
        """
        fields = super(NodeCreateSerializer, self).get_fields(*args, **kwargs)
        try:
            user = self.context['view'].request.user
        except KeyError: # avoid error when used out of Rest API
            return fields
        queryset = fields['group'].queryset
        if not user.is_superuser:
            msg = " Check if you have group or node administrator roles at the provided group."
            fields['group'].error_messages['does_not_exist'] += msg
            # bug #321: filter by user.id (None for Anonymous users)
            fields['group'].queryset = queryset.filter(allow_nodes=True,
                                        roles__user=user.id, roles__is_group_admin=True)
        return fields

class NodeSerializer(NodeCreateSerializer):
    class Meta:
        model = Node
        exclude = FW_CONFIG_FIELDS
        read_only_fields = ('group',)

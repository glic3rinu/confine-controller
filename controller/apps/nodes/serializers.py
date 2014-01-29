from __future__ import absolute_import

import json
import six

from api import serializers, exceptions
from api.validators import validate_properties

from . import settings
from .models import Server, Node, DirectIface


class ServerSerializer(serializers.UriHyperlinkedModelSerializer):
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


class NodeCreateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    properties = serializers.PropertyField(required=False)
    arch = serializers.ChoiceField(choices=settings.NODES_NODE_ARCHS, required=True)
    slivers = serializers.RelHyperlinkedRelatedField(many=True, read_only=True,
        view_name='sliver-detail')
    direct_ifaces = DirectIfaceSerializer(required=False, many=True, allow_add_remove=True)
    cert = serializers.Field()
    boot_sn = serializers.IntegerField(read_only=True)
    
    # FIXME #239 Remove firmware configuration cruft from data model
    # talk before with Axel and coordinate with Node firmware
    local_iface = serializers.CharField(required=True)
    sliver_pub_ipv6 = serializers.ChoiceField(choices=Node.IPV6_METHODS, required=True)
    sliver_pub_ipv4 = serializers.ChoiceField(choices=Node.IPV4_METHODS, required=True)
    sliver_pub_ipv4_range = serializers.CharField(required=True)
    
    class Meta:
        model = Node
        exclude = ('set_state',)
    
    def get_fields(self, *args, **kwargs):
        """
        Filter groups: the user creating this node must be an
        administrator or technician of this group, and the group
        must have node creation allowed (/allow_nodes=true).
        
        """
        fields = super(NodeCreateSerializer, self).get_fields(*args, **kwargs)
        try:
            user = self.context['view'].request.user
        except KeyError: # avoid error when used out of Rest API
            return fields
        queryset = fields['group'].queryset
        if not user.is_superuser:
            msg = " Check if you have administrator or technician roles at the provided group."
            fields['group'].error_messages['does_not_exist'] += msg
            # bug #321: filter by user.id (None for Anonymous users)
            fields['group'].queryset = queryset.filter(allow_nodes=True,
                                        roles__user=user.id, roles__is_admin=True)
        return fields
    
    def validate_properties(self, attrs, source):
        return validate_properties(self, attrs, source)

class NodeSerializer(NodeCreateSerializer):
    class Meta:
        model = Node
        read_only_fields = ('group',)

    def get_fields(self, *args, **kwargs):
        """ Filter states based on accepted transitions """
        fields = super(NodeSerializer, self).get_fields(*args, **kwargs)
        set_state = fields['set_state']
        try:
            state = self.object.set_state
        except AttributeError:
            # Is a querySet, readonly doesn't require filtering
            return fields
        # debug is an automatic state so doesnt accept changes
        if state == Node.DEBUG:
            set_state.read_only = True
        elif state == Node.FAILURE:
            set_state.choices = [(Node.SAFE, 'SAFE')]
        else: # SAFE or PRODUCTION
            is_debug = set_state.choices.pop(0)[0] == Node.DEBUG
            assert is_debug, "Problem removing DEBUG from set_state"
        return fields


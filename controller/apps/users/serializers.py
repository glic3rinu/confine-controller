from __future__ import absolute_import

from api import serializers
from users.models import User, Group, Roles, AuthToken


class GroupRolesSerializer(serializers.ModelSerializer):
    group = serializers.RelHyperlinkedRelatedField(view_name='group-detail')
    
    class Meta:
        model = Roles
        exclude = ['id', 'user']


class UserRolesSerializer(serializers.ModelSerializer):
    user = serializers.RelHyperlinkedRelatedField(view_name='user-detail')
    
    class Meta:
        model = Roles
        exclude = ['id', 'group']


class AuthTokenField(serializers.WritableField):
    def to_native(self, value):
        return [ token.data for token in value.all() ]


class UserSerializer(serializers.UriHyperlinkedModelSerializer):
    group_roles = GroupRolesSerializer(source='roles')
    auth_tokens = AuthTokenField()
    is_active = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = User
        exclude = ['password', 'groups']


class GroupSerializer(serializers.UriHyperlinkedModelSerializer):
    user_roles = UserRolesSerializer(source='roles')
    allow_nodes = serializers.BooleanField(read_only=True)
    allow_slices = serializers.BooleanField(read_only=True)
    slices = serializers.RelHyperlinkedRelatedField(many=True, source='slices',
        read_only=True, view_name='slice-detail')
    nodes = serializers.RelHyperlinkedRelatedField(many=True, source='nodes',
        read_only=True, view_name='node-detail')
    
    class Meta:
        model = Group

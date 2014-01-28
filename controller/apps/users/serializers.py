from __future__ import absolute_import

from django.core.exceptions import ValidationError

from api import serializers

from .models import User, Group, Roles


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


class UserCreateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    auth_tokens = AuthTokenField(required=False)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = User
        exclude = ['password', 'groups', 'username', 'email', 'is_active', 'is_superuser']


class UserSerializer(UserCreateSerializer, serializers.DynamicReadonlyFieldsModelSerializer):
    group_roles = GroupRolesSerializer(source='roles', required=False)
    is_active = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    
    class Meta:
        model = User
        exclude = ['password', 'groups', 'username', 'email']


class GroupCreateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    
    class Meta:
        model = Group
        exclude = ('allow_nodes', 'allow_slices', 'user_roles')


class GroupSerializer(GroupCreateSerializer, serializers.DynamicReadonlyFieldsModelSerializer):
    user_roles = UserRolesSerializer(source='roles', required=False, many=True)
    allow_nodes = serializers.BooleanField()
    allow_slices = serializers.BooleanField()
    slices = serializers.RelHyperlinkedRelatedField(many=True, source='slices',
        read_only=True, view_name='slice-detail')
    nodes = serializers.RelHyperlinkedRelatedField(many=True, source='nodes',
        read_only=True, view_name='node-detail')
    
    class Meta:
        model = Group
    
    def validate_user_roles(self, attrs, name):
        """ checks at least one admin per group """
        for role in attrs.get(name, []):
            if role.is_admin:
                return attrs
        raise ValidationError('The group must have at least one admin')


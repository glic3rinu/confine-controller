from __future__ import absolute_import

from rest_framework import serializers

from api.serializers import UriHyperlinkedModelSerializer, RelHyperlinkedRelatedField
from users.models import User, Group, Roles, AuthToken


class GroupRolesSerializer(serializers.ModelSerializer):
    group = RelHyperlinkedRelatedField(view_name='group-detail')
    
    class Meta:
        model = Roles
        exclude = ['id', 'user']


class UserRolesSerializer(serializers.ModelSerializer):
    user = RelHyperlinkedRelatedField(view_name='user-detail')
    
    class Meta:
        model = Roles
        exclude = ['id', 'group']


class AuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthToken
        exclude = ['id', 'group']


class UserSerializer(UriHyperlinkedModelSerializer):
    roles = GroupRolesSerializer()
    auth_tokens = AuthTokenSerializer()
    
    class Meta:
        model = User
        exclude = ['password', 'groups']


class GroupSerializer(UriHyperlinkedModelSerializer):
    roles = UserRolesSerializer()
    slices = RelHyperlinkedRelatedField(many=True, source='slices', view_name='slice-detail')
    nodes = RelHyperlinkedRelatedField(many=True, source='nodes', view_name='node-detail')
    
    class Meta:
        model = Group

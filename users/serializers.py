from rest_framework import serializers

from common.serializers import UriHyperlinkedModelSerializer, RelHyperlinkedRelatedField
from users.models import User, Group, Roles


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


class UserSerializer(UriHyperlinkedModelSerializer):
    group_roles = GroupRolesSerializer(source='roles_set')
    
    class Meta:
        model = User
        exclude = ['password', 'groups']


class GroupSerializer(UriHyperlinkedModelSerializer):
    user_roles = UserRolesSerializer(source='roles_set')
    
    class Meta:
        model = Group


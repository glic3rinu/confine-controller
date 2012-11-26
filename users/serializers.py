from rest_framework import serializers

from common.serializers import UriHyperlinkedModelSerializer
from users.models import User, Group, Roles


class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        exclude = ['user', 'id']


class UserSerializer(UriHyperlinkedModelSerializer):
    group_roles = RolesSerializer(source='roles_set')
    
    class Meta:
        model = User
        exclude = ['password', 'groups']


class GroupSerializer(UriHyperlinkedModelSerializer):
    user_roles = RolesSerializer(source='roles_set')
    
    class Meta:
        model = Group

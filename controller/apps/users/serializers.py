from __future__ import absolute_import

from api import serializers

from .models import AuthToken, User, Group, Roles


class GroupRolesSerializer(serializers.ModelSerializer):
    group = serializers.RelHyperlinkedRelatedField(view_name='group-detail')
    
    # Backwards compatibilty #414
    is_admin = serializers.Field(source='is_group_admin')
    is_technician = serializers.Field(source='is_node_admin')
    is_researcher = serializers.Field(source='is_slice_admin')
    
    class Meta:
        model = Roles
        exclude = ['id', 'user']
    
    def get_identity(self, data):
        try:
            group = data.get('group', {})
            return group.get('uri')
        except AttributeError:
            return None


class UserRolesSerializer(serializers.ModelSerializer):
    user = serializers.RelHyperlinkedRelatedField(view_name='user-detail')
    
    # Backwards compatibilty #414
    is_admin = serializers.Field(source='is_group_admin')
    is_technician = serializers.Field(source='is_node_admin')
    is_researcher = serializers.Field(source='is_slice_admin')
    
    class Meta:
        model = Roles
        exclude = ['id', 'group']
    
    def get_identity(self, data):
        try:
            group = data.get('user', {})
            return group.get('uri')
        except AttributeError:
            return None


class AuthTokenField(serializers.WritableField):
    def to_native(self, value):
        return [ token.data for token in value.all() ]
    
    def from_native(self, value):
        user_tokens = AuthToken.objects.filter(user=self.parent.object)
        auth_tokens = []
        for v in value:
            token = user_tokens.filter(data=v).first()
            if token is None:
                auth_tokens.append(AuthToken(data=v))
            else:
                user_tokens = user_tokens.exclude(pk=token.pk)
        # clean up old auth_tokens
        user_tokens.delete()
        return auth_tokens


class UserCreateSerializer(serializers.UriHyperlinkedModelSerializer):
    id = serializers.Field()
    auth_tokens = AuthTokenField(required=False)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = User
        exclude = ['password', 'groups', 'username', 'email', 'is_active', 'is_superuser']


class UserSerializer(UserCreateSerializer, serializers.DynamicReadonlyFieldsModelSerializer):
    group_roles = GroupRolesSerializer(source='roles', required=False, many=True, allow_add_remove=True)
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
    user_roles = UserRolesSerializer(source='roles', many=True, allow_add_remove=True)
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
            if role.is_group_admin:
                return attrs
        raise serializers.ValidationError('The group must have at least one admin')


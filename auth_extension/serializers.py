from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field()
    uuid = serializers.CharField()
    pubkey = serializers.CharField()
    description = serializers.CharField()
    auth_tokens = serializers.Field()
    
    class Meta:
        model = User
        exclude = ['groups', 'password', 'user_permissions']

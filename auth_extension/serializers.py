from auth_extension.models import UserProfile
from django.contrib.auth.models import User
from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['uuid', 'pubkey', 'description']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    userprofile = UserProfileSerializer()
    authtokens = serializers.Field()
    
    class Meta:
        model = User
        exclude = ['groups', 'password', 'user_permissions']

from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        exclude = ['password']

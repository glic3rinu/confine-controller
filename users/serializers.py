from common.serializers import UriHyperlinkedModelSerializer
from users.models import User, Group


class UserSerializer(UriHyperlinkedModelSerializer):
    class Meta:
        model = User
        exclude = ['password']


class GroupSerializer(UriHyperlinkedModelSerializer):
    class Meta:
        model = Group

from __future__ import absolute_import

from api import api, generics
from permissions.api import ApiPermissionsMixin

from .models import User, Group
from .serializers import UserSerializer, GroupSerializer


class UserList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.User.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#user_at_server)
    
    This resource lists the [users](http://wiki.confine-project.eu/arch:rest-api
    ?&#user_at_server) present in the testbed and provides API URIs to navigate
    to them.
    """
    model = User
    serializer_class = UserSerializer
#    filter_fields = ('username',)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.User.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#user_at_server)
    
    This resource describes a person using the testbed.
    """
    model = User
    serializer_class = UserSerializer


class GroupList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Group.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#group_at_server)
    
    This resource describes a group of users using the testbed.
    """
    model = Group
    serializer_class = GroupSerializer
#    filter_fields = ('username',)


class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Group.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#group_at_server)
    
    This resource describes a group of users using the testbed.
    """
    model = Group
    serializer_class = GroupSerializer


api.register(UserList, UserDetail)
api.register(GroupList, GroupDetail)

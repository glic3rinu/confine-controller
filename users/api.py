from rest_framework import generics

from common.api import api
from users.models import User
from users.serializers import UserSerializer


class UserList(generics.ListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.UserList.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#userlist_at_server)
    
    This resource lists the [users](http://wiki.confine-project.eu/arch:rest-api
    ?&#user_at_server) present in the testbed and provides API URIs to navigate 
    to them.
    """
    model = User
    serializer_class = UserSerializer
#    filter_fields = ('username',)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.User.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#user_at_server)
    
    This resource describes a person using the testbed.
    """
    model = User
    serializer_class = UserSerializer


api.register(UserList, UserDetail)

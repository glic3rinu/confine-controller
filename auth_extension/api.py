from auth_extension.serializers import UserSerializer
from common.api import api
from django.contrib.auth.models import User
from rest_framework import generics


class UserList(generics.ListCreateAPIView):
    """
    **Media type:** `application/vnd.confine.server.UserList.v0+json`
    
    This resource lists the users present in the testbed and provides API URIs 
    to navigate to them.
    """
    model = User
    serializer_class = UserSerializer
    filter_fields = ('username',)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** `application/vnd.confine.server.User.v0+json`
    
    This resource describes a person using the testbed.
    """
    model = User
    serializer_class = UserSerializer


api.register(UserList, UserDetail)

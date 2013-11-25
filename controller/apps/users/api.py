from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from api import api, generics
from permissions.api import ApiPermissionsMixin

from .models import User, Group
from .serializers import UserSerializer, GroupSerializer


class ChangePassword(APIView):
    """
    **Relation type:** [`http://confine-project.eu/rel/controller/do-change-password`](
        http://confine-project.eu/rel/controller/do-change-password)
    
    Endpoint containing the function URI used to reboot this node.
    
    POST data: `New user password`
    """
    url_name = 'change-password'
    rel = 'http://confine-project.eu/rel/controller/do-change-password'

    def post(self, request, *args, **kwargs):
        if request.DATA is not None:
            password = request.DATA
            if not password: # check if the password is empty
                raise exceptions.ParseError(detail='You must provide new password value')
            user = get_object_or_404(User, pk=kwargs.get('pk'))
            self.check_object_permissions(self.request, user)
            user.set_password(password)
            user.save()
            response_data = {'detail': 'User password changed successfully'}
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        raise exceptions.ParseError(detail='You must provide new password value')


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
    ctl = [ChangePassword]


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

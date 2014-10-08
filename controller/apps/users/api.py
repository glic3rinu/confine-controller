from __future__ import absolute_import

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api import api, generics
from permissions.api import ApiPermissionsMixin

from .models import User, Group, Roles
from .renderers import GroupProfileRenderer, UserProfileRenderer
from .serializers import (GroupSerializer, GroupCreateSerializer,
    UserSerializer, UserCreateSerializer)


class ChangeAuth(APIView):
    """
    **Relation type:** [`http://confine-project.eu/rel/controller/do-change-auth`](
        http://confine-project.eu/rel/controller/do-change-auth)
    
    Endpoint containing the function URI used to change the user auth.
    
    POST data: `New user authentication data:
        - email (optional)
        - username (optional)
        - password (required)`
    """
    url_name = 'change-auth'
    rel = 'http://confine-project.eu/rel/controller/do-change-auth'
    
    def post(self, request, *args, **kwargs):
        email = request.DATA.get('email', None)
        username = request.DATA.get('username', None)
        password = request.DATA.get('password', None)
        if password:
            fields_updated = ['password']
            exclude = ['username', 'email']
            user = get_object_or_404(User, pk=kwargs.get('pk'))
            self.check_object_permissions(self.request, user)
            user.set_password(password)
            # set optional fields
            for opt_field in ['username', 'email']:
                if eval(opt_field):
                    setattr(user, opt_field, eval(opt_field))
                    fields_updated.append(opt_field)
                    exclude.remove(opt_field)
            # validate data
            try:
                user.clean_fields(exclude=exclude)
            except ValidationError as e:
                raise exceptions.ParseError(detail='; '.join(e.messages))
            user.save()
            response_data = {
                'detail': 'User %s changed successfully' % ', '.join(fields_updated)
            }
            return Response(response_data, status=status.HTTP_200_OK)
        raise exceptions.ParseError(detail='Password value not provided')


class UserList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/resource-list"`](
        http://wiki.confine-project.eu/arch:rest-api#user_at_registry)
    
    This resource lists the [users](http://wiki.confine-project.eu/arch:rest-
    api#user_at_registry) present in the testbed and provides API URIs to
    navigate to them.
    """
    model = User
    add_serializer_class = UserCreateSerializer
    serializer_class = UserSerializer

    def pre_save(self, obj):
        super(UserList, self).pre_save(obj)
        if not obj.email:
            obj.email = "%s@localhost" % obj.name


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/user"`](
        http://wiki.confine-project.eu/arch:rest-api#user_at_registry)
    
    This resource describes a person using the testbed.
    """
    model = User
    serializer_class = UserSerializer
    ctl = [ChangeAuth]
    fields_superuser = ['is_active', 'is_superuser']
    renderer_classes = [UserProfileRenderer, BrowsableAPIRenderer]


class GroupList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/resource-list"`](
        http://wiki.confine-project.eu/arch:rest-api#group_at_registry)
    
    This resource lists the [groups](http://wiki.confine-project.eu/arch:rest-
    api#group_at_registry) present in the testbed and provides API URIs to
    navigate to them.
    """
    model = Group
    add_serializer_class = GroupCreateSerializer
    serializer_class = GroupSerializer
    
    def post_save(self, obj, created=False):
        """ user that creates a group becomes its admin """
        Roles.objects.get_or_create(user=self.request.user, group=obj, is_group_admin=True)


class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/group"`](
        http://wiki.confine-project.eu/arch:rest-api#group_at_registry)
    
    This resource describes a group of users using the testbed.
    """
    model = Group
    serializer_class = GroupSerializer
    fields_superuser = ['allow_nodes', 'allow_slices']
    renderer_classes = [GroupProfileRenderer, BrowsableAPIRenderer]


api.register(UserList, UserDetail)
api.register(GroupList, GroupDetail)

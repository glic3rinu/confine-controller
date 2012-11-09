from auth_extension.serializers import UserSerializer
from common.api import api
from django.contrib.auth.models import User
from rest_framework import generics


class UserList(generics.ListCreateAPIView):
    model = User
    serializer_class = UserSerializer
    filter_fields = ('username',)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    model = User
    serializer_class = UserSerializer


api.register(UserList, UserDetail)

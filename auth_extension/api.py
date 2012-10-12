from auth_extension.serializers import UserSerializer
from controller import api
from django.contrib.auth.models import User
from rest_framework import generics


class Users(generics.ListCreateAPIView):
    model = User
    serializer_class = UserSerializer


class User(generics.RetrieveUpdateDestroyAPIView):
    model = User
    serializer_class = UserSerializer


api.register((Users, User), 'user')

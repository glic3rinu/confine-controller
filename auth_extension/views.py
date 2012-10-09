from auth_extension.serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import generics


class UserRoot(generics.ListCreateAPIView):
    model = User
    serializer_class = UserSerializer


class UserInstance(generics.RetrieveUpdateDestroyAPIView):
    model = User
    serializer_class = UserSerializer


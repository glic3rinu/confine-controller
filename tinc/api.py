from controller import api
from rest_framework import generics
from tinc.models import Island, Host
from tinc.serializers import IslandSerializer, HostSerializer


class IslandList(generics.ListCreateAPIView):
    model = Island
    serializer_class = IslandSerializer


class IslandDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Island
    serializer_class = IslandSerializer


class HostList(generics.ListCreateAPIView):
    model = Host
    serializer_class = HostSerializer


class HostDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Host
    serializer_class = HostSerializer


api.register((IslandList, IslandDetail))
api.register((HostList, HostDetail))

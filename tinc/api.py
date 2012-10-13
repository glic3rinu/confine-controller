from apis import rest
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


rest.api.register(IslandList, IslandDetail)
rest.api.register(HostList, HostDetail)

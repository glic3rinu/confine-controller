from common.api import api
from rest_framework import generics
from tinc.models import Island, Host, Gateway
from tinc.serializers import IslandSerializer, HostSerializer, GatewaySerializer


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


class GatewayList(generics.ListCreateAPIView):
    model = Gateway
    serializer_class = GatewaySerializer


class GatewayDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Gateway
    serializer_class = GatewaySerializer


api.register(IslandList, IslandDetail)
api.register(HostList, HostDetail)
api.register(GatewayList, GatewayDetail)

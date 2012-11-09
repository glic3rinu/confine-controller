from common.api import api
from rest_framework import generics
from tinc.models import Island, Host, Gateway
from tinc.serializers import IslandSerializer, HostSerializer, GatewaySerializer


class IslandList(generics.ListCreateAPIView):
    """
    **Media type:** `application/vnd.confine.server.IslandList.v0+json`
    
    This resource lists the network islands supported by the testbed and provides 
    API URIs to navigate to them.
    """
    model = Island
    serializer_class = IslandSerializer


class IslandDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** `application/vnd.confine.server.Island.v0+json`
    
    This resource describes a network island (i.e. a disconnected part of a 
    community network) where the testbed is reachable from. A testbed is reachable 
    from an island when there is a gateway that gives access to the testbed server 
    (possibly through other gateways), or when the server itself is in that island.
    """
    model = Island
    serializer_class = IslandSerializer


class HostList(generics.ListCreateAPIView):
    """
    **Media type:** `application/vnd.confine.server.HostList.v0+json`
    
    This resource lists odd hosts connected to the testbed (through the management 
    network) and provides API URIs to navigate to them.
    """
    model = Host
    serializer_class = HostSerializer


class HostDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** `application/vnd.confine.server.Host.v0+json`
    
    This resource describes an odd host computer connected to the testbed (through 
    the management network) with a known administrator.
    """
    model = Host
    serializer_class = HostSerializer


class GatewayList(generics.ListCreateAPIView):
    """
    **Media type:** `application/vnd.confine.server.GatewayList.v0+json`
    
    This resource lists testbed gateways and provides API URIs to navigate to them.
    """
    model = Gateway
    serializer_class = GatewaySerializer


class GatewayDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** `application/vnd.confine.server.Gateway.v0+json`
    
    This resource describes a network gateway providing access to the testbed 
    server and listening on tinc addresses on one or more community network 
    islands. The gateway connects to other gateways or the testbed server in 
    order to reach the later.
    """
    model = Gateway
    serializer_class = GatewaySerializer


api.register(IslandList, IslandDetail)
api.register(HostList, HostDetail)
api.register(GatewayList, GatewayDetail)

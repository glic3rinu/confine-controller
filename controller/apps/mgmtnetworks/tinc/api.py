from __future__ import absolute_import

from api import api, generics
from permissions.api import ApiPermissionsMixin

from .models import Island, Host, Gateway
from .serializers import IslandSerializer, HostSerializer, GatewaySerializer


class IslandList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Island.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#island_at_server)
    
    This resource lists the network [islands](http://wiki.confine-project.eu/
    arch:rest-api?&#island_at_server) supported by the testbed and provides
    API URIs to navigate to them.
    """
    model = Island
    serializer_class = IslandSerializer


class IslandDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Island.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#island_at_server)
    
    This resource describes a network island (i.e. a disconnected part of a
    community network) where the testbed is reachable from. A testbed is reachable
    from an island when there is a [gateway](http://wiki.confine-project.eu/arch
    :rest-api?&#gateway_at_server) that gives access to the testbed server
    (possibly through other gateways), or when the [server](https://wiki.confine
    -project.eu/arch:rest-api?&#server_at_server) itself is in that island.
    """
    model = Island
    serializer_class = IslandSerializer


class HostList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.HostList.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#hostlist_at_server)
    
    This resource lists odd [hosts](http://wiki.confine-project.eu/arch:rest-
    api?&#host_at_server) connected to the testbed (through the management
    network) and provides API URIs to navigate to them.
    """
    model = Host
    serializer_class = HostSerializer


class HostDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Host.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#host_at_server)
    
    This resource describes an odd host computer connected to the testbed (through
    the management network) with a known administrator.
    """
    model = Host
    serializer_class = HostSerializer


class GatewayList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Gateway.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#gateway_at_server)
    
    This resource lists testbed [gateways](http://wiki.confine-project.eu/arch:
    rest-api?&#gateway_at_server) and provides API URIs to navigate to them.
    """
    model = Gateway
    serializer_class = GatewaySerializer


class GatewayDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Gateway.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#gateway_at_server)
    
    This resource describes a network gateway providing access to the testbed
    [server](http://wiki.confine-project.eu/arch:rest-api?&#server_at_server)
    and listening on tinc addresses on one or more community network
    [islands](http://wiki.confine-project.eu/arch:rest-api?&#island_at_server).
    The gateway connects to other gateways or the testbed server in
    order to reach the later.
    """
    model = Gateway
    serializer_class = GatewaySerializer


api.register(IslandList, IslandDetail)
api.register(HostList, HostDetail)
api.register(GatewayList, GatewayDetail)

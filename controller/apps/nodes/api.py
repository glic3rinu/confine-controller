from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from api import api, generics
from permissions.api import ApiPermissionsMixin

from .models import Island, Node, Server
from .serializers import (IslandSerializer, NodeSerializer, NodeCreateSerializer,
    ServerSerializer)
from .settings import NODES_NODE_API_NODE_BASE_URL
from .validators import validate_csr


class Reboot(APIView):
    """
    **Relation type:** [`http://confine-project.eu/rel/server/do-reboot`](
        http://confine-project.eu/rel/server/do-reboot)
    
    Endpoint containing the function URI used to reboot this node.
    
    POST data: `null`
    """
    url_name = 'reboot'
    rel = 'http://confine-project.eu/rel/server/do-reboot'
    
    def post(self, request, *args, **kwargs):
        if not request.DATA:
            node = get_object_or_404(Node, pk=kwargs.get('pk'))
            self.check_object_permissions(self.request, node)
            node.reboot()
            response_data = {'detail': 'Node instructed to reboot'}
            return Response(response_data, status=status.HTTP_200_OK)
        raise exceptions.ParseError(detail='This endpoint do not accept data')


class RequestCert(APIView):
    """
    **Relation type:** [`http://confine-project.eu/rel/controller/do-request-cert`](
        http://confine-project.eu/rel/controller/do-request-cert)
    
    Contains the function URI used to upload this node's certificate request to 
    be signed by the testbed CA and set as the node's certificate.
    
    POST data: `ASCII-armored PEM representation of the CSR as a string.`
    """
    url_name = 'request-cert'
    rel = 'http://confine-project.eu/rel/controller/do-request-api-cert'
    
    def post(self, request, *args, **kwargs):
        csr = request.DATA
        node = get_object_or_404(Node, pk=kwargs.get('pk'))
        self.check_object_permissions(self.request, node)
        try:
            validate_csr(csr, node)
        except:
            raise exceptions.ParseError(detail='Malformed CSR')
        node.sign_cert_request(csr.strip())
        response_data = {'detail': 'Sign certificate request accepted'}
        return Response(response_data, status=status.HTTP_202_ACCEPTED)


class NodeList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """ 
    **Media type:** [`application/vnd.confine.server.Node.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#node_at_server)
    
    This resource lists the [nodes](http://wiki.confine-project.eu/arch:rest-
    api?&#node_at_server) available in the testbed and provides API URIs to
    navigate to them.
    """
    model = Node
    add_serializer_class = NodeCreateSerializer
    serializer_class = NodeSerializer
    filter_fields = ('arch', 'set_state', 'group', 'group__name')


class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Node.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#node_at_server)
    
    This resource describes a node in the testbed as well as listing the
    [slivers](http://wiki.confine-project.eu/arch:rest-api?&#sliver_at_server)
    intended to run on it with API URIs to navigate to them.
    """
    model = Node
    serializer_class = NodeSerializer
    ctl = [Reboot, RequestCert]
    
    def get(self, request, *args, **kwargs):
        """ Add node-base relation to link header """
        response = super(NodeDetail, self).get(request, *args, **kwargs)
        node = self.get_object()
        url = NODES_NODE_API_NODE_BASE_URL % {'mgmt_addr': node.mgmt_net.addr}
        rel = 'http://confine-project.eu/rel/server/node-base'
        response['Link'] += ', <%s>; rel="%s"' % (url, rel)
        return response


class ServerDetail(generics.RetrieveUpdateDestroyAPIView):
    """ 
    **Media type:** [`application/vnd.confine.server.Server.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#server_at_server)
    
    This resource describes the testbed server (controller).
    """
    model = Server
    serializer_class = ServerSerializer
    
    def get_object(self, *args, **kwargs):
        return get_object_or_404(Server)


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


api.register(NodeList, NodeDetail)
api.register(ServerDetail, ServerDetail)
api.register(IslandList, IslandDetail)

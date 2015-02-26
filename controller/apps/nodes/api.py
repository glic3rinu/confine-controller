from __future__ import absolute_import

from django.core import management
from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from controller.utils.apps import is_installed

from api import api, generics
from permissions.api import ApiPermissionsMixin

from .models import Island, Node, Server
from .renderers import (IslandProfileRenderer, NodeProfileRenderer,
    ServerProfileRenderer)
from .serializers import (IslandSerializer, NodeSerializer, NodeCreateSerializer,
    ServerSerializer)
from .settings import NODES_NODE_API_BASE_URI_DEFAULT


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


class NodeList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """ 
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/resource-list"`](
        http://wiki.confine-project.eu/arch:rest-api#node_at_registry)
    
    This resource lists the [nodes](http://wiki.confine-project.eu/arch:rest-
    api#node_at_registry) available in the testbed and provides API URIs to
    navigate to them.
    """
    model = Node
    add_serializer_class = NodeCreateSerializer
    serializer_class = NodeSerializer
    filter_fields = ('arch', 'set_state', 'group', 'group__name')
    
    def post_save(self, obj, created=False):
        if created and is_installed('resources'):
            management.call_command('syncresources')


class NodeDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/node"`](
        http://wiki.confine-project.eu/arch:rest-api#node_at_registry)
    
    This resource describes a node in the testbed as well as listing the
    [slivers](http://wiki.confine-project.eu/arch:rest-api?&#sliver_at_registry)
    intended to run on it with API URIs to navigate to them.
    """
    model = Node
    serializer_class = NodeSerializer
    renderer_classes = [NodeProfileRenderer, BrowsableAPIRenderer]
    ctl = [Reboot]
    
    def get(self, request, *args, **kwargs):
        """ Add node-base relation to link header """
        response = super(NodeDetail, self).get(request, *args, **kwargs)
        node = self.get_object()
        url = NODES_NODE_API_BASE_URI_DEFAULT % {'mgmt_addr': node.mgmt_net.addr}
        rel = 'http://confine-project.eu/rel/server/node-base'
        response['Link'] += ', <%s>; rel="%s"' % (url, rel)
        return response


class ServerList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Server.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#server_at_server)
    
    This resource lists the [nodes](http://wiki.confine-project.eu/arch:rest-
    api?&#server_at_server) available in the testbed and provides API URIs to
    navigate to them.
    """
    model = Server
    serializer_class = ServerSerializer


class ServerDetail(generics.RetrieveUpdateDestroyAPIView):
    """ 
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/server"`](
        http://wiki.confine-project.eu/arch:rest-api#server_at_registry)
    
    This resource describes the testbed server (controller).
    """
    model = Server
    serializer_class = ServerSerializer
    renderer_classes = [ServerProfileRenderer, BrowsableAPIRenderer]


# backwards compatibility default server #236
class ServerDefaultDetail(ServerDetail):
    def get_object(self, *args, **kwargs):
        return get_object_or_404(Server, pk=2)


class IslandList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/resource-list"`](
        http://wiki.confine-project.eu/arch:rest-api#island_at_registry)
    
    This resource lists the network [islands](http://wiki.confine-project.eu/
    arch:rest-api#island_at_registry) supported by the testbed and provides
    API URIs to navigate to them.
    """
    model = Island
    serializer_class = IslandSerializer


class IslandDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/island"`](
        http://wiki.confine-project.eu/arch:rest-api#island_at_registry)
    
    This resource describes a network island, i.e. a possibly disconnected part
    of a community network. The usage of islands is mainly orientative: it can
    be used to signal user interfaces whether a node may see any servers, or
    whether modifying a gateway may leave some nodes disconnected from the
    testbed management network.
    """
    model = Island
    serializer_class = IslandSerializer
    renderer_classes = [IslandProfileRenderer, BrowsableAPIRenderer]


api.register(NodeList, NodeDetail)
api.register(ServerList, ServerDetail)
api.register(IslandList, IslandDetail)

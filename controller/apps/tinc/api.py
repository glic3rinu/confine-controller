from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api import api, generics
from api.renderers import ResourceListJSONRenderer
from permissions.api import ApiPermissionsMixin

from .models import Host, Gateway
from .renderers import GatewayProfileRenderer, HostProfileRenderer
from .serializers import HostCreateSerializer, HostSerializer, GatewaySerializer


class UploadPubkey(APIView):
    """
    HACK ENDPOINT
    """
    url_name = 'upload-pubkey'
    rel = 'http://confine-project.eu/rel/controller/do-upload-pubkey'
    
    def post(self, request, *args, **kwargs):
        pubkey = request.DATA
        if pubkey:
            host = get_object_or_404(Host, pk=kwargs.get('pk'))
            self.check_object_permissions(self.request, host)
            tinchost = host.related_tinchost.first()
            tinchost.pubkey = pubkey
            tinchost.save()
            response_data = {'detail': 'host pubkey changed successfully'}
            return Response(response_data, status=status.HTTP_200_OK)
        raise exceptions.ParseError(detail='pubkey value not provided')


class HostList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/resource-list"`](
        http://wiki.confine-project.eu/arch:rest-api#host_at_registry)
    
    This resource lists odd [hosts](http://wiki.confine-project.eu/arch:rest-
    api#host_at_registry) connected to the testbed (through the management
    network) and provides API URIs to navigate to them.
    """
    model = Host
    add_serializer_class = HostCreateSerializer
    serializer_class = HostSerializer
    renderer_classes = [ResourceListJSONRenderer, BrowsableAPIRenderer]
    
    def pre_save(self, obj):
        """ Set the object's owner, based on the incoming request. """
        obj.owner = self.request.user


class HostDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/host"`](
        http://wiki.confine-project.eu/arch:rest-api#host_at_registry)
    
    This resource describes an odd host computer connected to the testbed (through
    the management network) with a known administrator.
    """
    model = Host
    serializer_class = HostSerializer
    renderer_classes = [HostProfileRenderer, BrowsableAPIRenderer]
    ctl = [UploadPubkey]


class GatewayList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/resource-list"`](
        http://wiki.confine-project.eu/arch:rest-api#gateway_at_registry)
    
    This resource lists testbed [gateways](http://wiki.confine-project.eu/arch:
    rest-api#gateway_at_registry) and provides API URIs to navigate to them.
    """
    model = Gateway
    serializer_class = GatewaySerializer
    renderer_classes = [ResourceListJSONRenderer, BrowsableAPIRenderer]


class GatewayDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v0/gateway"`](
        http://wiki.confine-project.eu/arch:rest-api#gateway_at_registry)
    
    This resource describes a network gateway providing access to the testbed
    [server](http://wiki.confine-project.eu/arch:rest-api#server_at_registry)
    and listening on tinc addresses on one or more community network
    [islands](http://wiki.confine-project.eu/arch:rest-api#island_at_registry).
    The gateway connects to other gateways or the testbed server in
    order to reach the later.
    """
    model = Gateway
    serializer_class = GatewaySerializer
    renderer_classes = [GatewayProfileRenderer, BrowsableAPIRenderer]


api.register(HostList, HostDetail)
api.register(GatewayList, GatewayDetail)

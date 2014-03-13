from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from api import api, generics
from permissions.api import ApiPermissionsMixin

from .models import Host, Gateway
from .serializers import HostSerializer, GatewaySerializer


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
            tincclient = host.related_tincclient.all()[0]
            tincclient.pubkey=pubkey
            tincclient.save()
            response_data = {'detail': 'host pubkey changed successfully'}
            return Response(response_data, status=status.HTTP_200_OK)
        raise exceptions.ParseError(detail='pubkey value not provided')


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
    
    def post(self, request, *args, **kwargs):
        """ adds current request.user as default host owner """
        request.DATA['owner'] = {
            'uri': reverse('user-detail', args=[request.user.pk], request=request)
        }
        return super(HostList, self).post(request, *args, **kwargs)


class HostDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Host.v0+json`](
        http://wiki.confine-project.eu/arch:rest-api?&#host_at_server)
    
    This resource describes an odd host computer connected to the testbed (through
    the management network) with a known administrator.
    """
    model = Host
    serializer_class = HostSerializer
    ctl = [UploadPubkey]


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


api.register(HostList, HostDetail)
api.register(GatewayList, GatewayDetail)

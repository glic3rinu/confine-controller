from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api import api, generics
from permissions.api import ApiPermissionsMixin

from .models import Host
from .serializers import HostCreateSerializer, HostSerializer
from .renderers import HostProfileRenderer


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
        profile="http://confine-project.eu/schema/registry/v1/resource-list"`](
        http://wiki.confine-project.eu/arch:rest-api#host_at_registry)
    
    This resource lists odd [hosts](http://wiki.confine-project.eu/arch:rest-
    api#host_at_registry) connected to the testbed (through the management
    network) and provides API URIs to navigate to them.
    """
    model = Host
    add_serializer_class = HostCreateSerializer
    serializer_class = HostSerializer
    
    def pre_save(self, obj):
        """ Set the object's owner, based on the incoming request. """
        obj.owner = self.request.user


class HostDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/registry/v1/host"`](
        http://wiki.confine-project.eu/arch:rest-api#host_at_registry)
    
    This resource describes an odd host computer connected to the testbed (through
    the management network) with a known administrator.
    """
    model = Host
    serializer_class = HostSerializer
    renderer_classes = [HostProfileRenderer, BrowsableAPIRenderer]
    ctl = [UploadPubkey]


api.register(HostList, HostDetail)

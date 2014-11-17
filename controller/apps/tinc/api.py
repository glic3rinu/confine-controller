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
        profile="http://confine-project.eu/schema/registry/v0/resource-list"`](
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
        profile="http://confine-project.eu/schema/registry/v0/host"`](
        http://wiki.confine-project.eu/arch:rest-api#host_at_registry)
    
    This resource describes an odd host computer connected to the testbed (through
    the management network) with a known administrator.
    """
    model = Host
    serializer_class = HostSerializer
    renderer_classes = [HostProfileRenderer, BrowsableAPIRenderer]
    ctl = [UploadPubkey]


api.register(HostList, HostDetail)


# backwards compatibility #245 note-42
import json
from api import ApiRoot
from api.utils import link_header
from controller.utils import get_project_root
from django.core.urlresolvers import reverse
from django.http import Http404
from os import path
from rest_framework.decorators import api_view


def get_headers(request):
    base_link = [
        ('base', ApiRoot.REGISTRY_REL_PREFIX + 'base'),
        ('base_controller', ApiRoot.CONTROLLER_REL_PREFIX + 'base'),
    ]
    return {'Link': link_header(base_link, request)}


def load_gateways_snapshot(request):
    """
    Read snapshot file and load gateways.
    
    Backwards compatibility data stored during upgrade by
    controller/management/commands/postupgradecontroller.py
    """
    gateways_file = path.join(get_project_root(), 'gateways.api.json')
    gateways = []
    try:
        data = open(gateways_file, "r").read()
    except IOError:
        pass # Doesn't exist gateway backup
    else:
        try:
            gateways = json.loads(data)
        except ValueError:
            pass # Invalid format
        else:
            for gw in gateways:
                gw_url = reverse('gateway-detail', kwargs={'pk':gw['id']})
                gw['uri'] = request.build_absolute_uri(gw_url)
    
    return gateways
    

@api_view(['GET'])
def gateway_list(request):
    headers = get_headers(request)
    gateways = load_gateways_snapshot(request)
    return Response(gateways, headers=headers)


@api_view(['GET'])
def gateway_detail(request, pk):
    # verify object pk
    try:
        pk = int(pk)
    except (TypeError, ValueError):
        raise Http404
    
    # try load gateway data from snapshot
    headers = get_headers(request)
    gateways = load_gateways_snapshot(request)
    for gw in gateways:
        if gw['id'] == pk:
            return Response(gw, headers=headers)
    
    raise Http404

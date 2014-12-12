from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response

from api import api, generics
from api.utils import insert_ctl
from nodes.api import NodeDetail
from nodes.models import Node, Server, ServerApi
from permissions.api import ApiPermissionsMixin

from .exceptions import BaseImageNotAvailable, ConcurrencyError
from .models import BaseImage, Build, Config
from .renderers import BaseImageProfileRenderer
from .serializers import (BaseImageSerializer, FirmwareSerializer,
    NodeFirmwareConfigSerializer)


class BaseImageList(ApiPermissionsMixin, generics.URIListCreateAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/controller/v0/resource-list"`](
        http://wiki.confine-project.eu/arch:rest-api#baseimage_at_controller)
    """
    model = BaseImage
    serializer_class = BaseImageSerializer
    controller_view = True
    # TODO customize rest_to_admin_url --> admin:firmware_config_change


class BaseImageDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/json;
        profile="http://confine-project.eu/schema/controller/v0/baseimage"`](
        http://wiki.confine-project.eu/arch:rest-api#baseimage_at_controller)
    """
    model = BaseImage
    serializer_class = BaseImageSerializer
    renderer_classes = [BaseImageProfileRenderer, BrowsableAPIRenderer]
    controller_view = True


class Firmware(generics.RetrieveUpdateDestroyAPIView):
    url_name = 'firmware'
    rel = 'http://confine-project.eu/rel/controller/firmware'
    serializer_class = FirmwareSerializer
    model = Build
    list = False
    
    def post(self, request, pk, *args, **kwargs):
        node = get_object_or_404(Node, pk=pk)
        data = request.DATA or {}
        
        fw_config = NodeFirmwareConfigSerializer(node, data=data)
        if not fw_config.is_valid():
            raise exceptions.ParseError(detail=fw_config.errors)
        
        ### Initialize defaults ###
        kwargs = fw_config.data
        base_image = BaseImage.objects.get(pk=kwargs.pop('base_image'))
        async = True
        success_status = status.HTTP_202_ACCEPTED
        
        # allow asynchronous requests
        if '201-created' == request.META.get('HTTP_EXPECT', None):
            async = False
            success_status = status.HTTP_201_CREATED
        
        ### call firmware build task ###
        try:
            build = Build.build(node, base_image, async=async, **kwargs)
        except ConcurrencyError as e:
            raise exceptions.Throttled(detail=e.message)
        
        serializer = self.serializer_class(build)
        return Response(serializer.data, status=success_status)


insert_ctl(NodeDetail, Firmware)
api.register(BaseImageList, BaseImageDetail)

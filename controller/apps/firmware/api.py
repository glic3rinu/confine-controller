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
        errors = {}
        kwargs = {}
        
        fw_config = NodeFirmwareConfigSerializer(node, data=data)
        if fw_config.is_valid():
            kwargs.update(fw_config.data)
        else:
            errors.update(fw_config.errors)
        
        # get plugins configuration
        config = Config.objects.get()
        for plugin in config.plugins.active():
            serializer_class = plugin.instance.get_serializer()
            if serializer_class:
                serializer = serializer_class(node, data=data)
                if serializer.is_valid():
                    kwargs.update(serializer.process_post())
                else:
                    errors.update(serializer.errors)
        if errors:
            raise exceptions.ParseError(detail=errors)
        
        # initialize firmware configuration
        base_image = BaseImage.objects.get(pk=kwargs.pop('base_image_id'))
        async = True
        success_status = status.HTTP_202_ACCEPTED
        
        # allow asynchronous requests
        if '201-created' == request.META.get('HTTP_EXPECT', None):
            async = False
            success_status = status.HTTP_201_CREATED
        
        # call firmware build task
        try:
            build = Build.build(node, base_image, async=async, **kwargs)
        except ConcurrencyError as e:
            raise exceptions.Throttled(detail=e.message)
        
        serializer = self.serializer_class(build)
        return Response(serializer.data, status=success_status)


insert_ctl(NodeDetail, Firmware)
api.register(BaseImageList, BaseImageDetail)

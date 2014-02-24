from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from api import generics
from api.utils import insert_ctl
from nodes.api import NodeDetail
from nodes.models import Node

from .exceptions import BaseImageNotAvailable
from .models import Build, Config
from .serializers import FirmwareSerializer


class Firmware(generics.RetrieveUpdateDestroyAPIView):
    url_name = 'firmware'
    rel = 'http://confine-project.eu/rel/controller/firmware'
    serializer_class = FirmwareSerializer
    model = Build
    list = False
    
    def post(self, request, pk, *args, **kwargs):
        node = get_object_or_404(Node, pk=pk)
        if not request.DATA:
            config = get_object_or_404(Config)
            base_image = config.get_images(node).order_by('-default').first()
            if base_image is None:
                raise BaseImageNotAvailable
            async = True
            success_status = status.HTTP_202_ACCEPTED
            if '201-created' == request.META.get('HTTP_EXPECT', None):
                async = False
                success_status = status.HTTP_201_CREATED
            build = Build.build(node, base_image, async=async)
            serializer = self.serializer_class(build, data=request.DATA)
            return Response(serializer.data, status=success_status)
        raise exceptions.ParseError(detail='This endpoint only accepts null data')


insert_ctl(NodeDetail, Firmware)

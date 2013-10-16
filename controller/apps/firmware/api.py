from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from api import generics
from api.utils import insert_ctl
from nodes.api import NodeDetail
from nodes.models import Node

from .models import Build, Config
from .serializers import FirmwareSerializer


class Firmware(generics.RetrieveUpdateDestroyAPIView):
    url_name = 'firmware'
    serializer_class = FirmwareSerializer
    model = Build
    
    def post(self, request, pk, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            config = get_object_or_404(Config)
            node = get_object_or_404(Node, pk=pk)
            base_image = config.get_images(node).order_by('default')[0]
            build = Build.build(node, base_image, async=True)
            serializer = self.serializer_class(build, data=request.DATA)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


insert_ctl(NodeDetail, Firmware)

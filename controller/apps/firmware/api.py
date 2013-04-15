from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from api import api, generics
from api.utils import insert_ctl
from nodes.api import NodeDetail
from nodes.models import Node
from permissions.api import ApiPermissionsMixin

from .models import Build
from .serializers import FirmwareSerializer



class Firmware(APIView):
    url_name = 'firmware'
    
    def get(self, request, pk, format=None):
        node = get_object_or_404(Node, pk=pk)
        try:
            build = node.build
        except:
            build = Build()
        serializer = FirmwareSerializer(build, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        pass
    
    def delete(self, request, pk, format=None):
        pass


insert_ctl(NodeDetail, Firmware)

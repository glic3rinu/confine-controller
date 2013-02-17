from __future__ import absolute_import

from rest_framework import serializers

from api import api
from controller.utils import is_installed
from nodes.models import Server, Node

from .models import CnHost


class CnHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CnHost
        exclude = ['id', 'content_type', 'object_id']


api.aggregate(Node, CnHostSerializer, name='cn')
api.aggregate(Server, CnHostSerializer, name='cn')



if is_installed('mgmtnetworks.tinc'):
    from mgmtnetworks.tinc.models import Gateway
    api.aggregate(Gateway, CnHostSerializer, name='cn')

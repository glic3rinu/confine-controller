from django.conf import settings as project_settings
from rest_framework import serializers

from common.api import api
from nodes.models import Server, Node
from .models import CnHost


class CnHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CnHost
        exclude = ['id', 'content_type', 'object_id']


api.aggregate(Node, CnHostSerializer, name='cn')
api.aggregate(Server, CnHostSerializer, name='cn')


if 'tinc' in project_settings.INSTALLED_APPS:
    from tinc.models import Gateway
    api.aggregate(Gateway, CnHostSerializer, name='cn')

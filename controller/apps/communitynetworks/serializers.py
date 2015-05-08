from __future__ import absolute_import

from rest_framework import serializers

from controller.apps.api import api
from controller.apps.nodes.models import Server, Node

from .models import CnHost


class CnHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CnHost
        exclude = ['id', 'content_type', 'object_id', 'cndb_cached_on']


# TODO: POST/PUT this resource fails. Related info:
# https://groups.google.com/forum/#!topic/django-rest-framework/2iEat5mCbvY/discussion
api.aggregate(Node, CnHostSerializer, name='cn', required=False)
api.aggregate(Server, CnHostSerializer, name='cn', required=False)

from __future__ import absolute_import

from api import api, serializers
from nodes.models import Node
from slices.models import Slice
from users.models import User, Group

from .models import SfaObject


class SfaObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SfaObject
        exclude = ('object_id', 'content_type', 'id')

# TODO /sfa writable -> UUID only writable on creation, once set cannot be changed

for model in [Node, User, Group, Slice]:
    api.aggregate(model, SfaObjectSerializer, name='sfa')

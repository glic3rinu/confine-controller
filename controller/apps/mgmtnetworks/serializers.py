from __future__ import absolute_import

from api import api, serializers
from nodes.models import Server, Node

from .models import MgmtNetConf


class MgmtNetConfSerializer(serializers.ModelSerializer):
    addr = serializers.Field()
    backend = serializers.CharField()

    ## backwards compatibility #157
    tinc_client = serializers.Field()
    tinc_server = serializers.Field()
    native = serializers.Field()
    
    class Meta:
        model = MgmtNetConf
        exclude = ('id', 'content_type', 'object_id')


# Aggregate mgmt_network to the API
for model in [Server, Node]:
    api.aggregate(model, MgmtNetConfSerializer, name='mgmt_net')

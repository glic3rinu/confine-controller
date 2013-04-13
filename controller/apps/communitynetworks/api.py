from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils import insert_ctl

from nodes.models import Node
from nodes.api import NodeDetail


class CacheCNDB(APIView):
    """
    **Relation type:** [`http://confine-project.eu/rel/server/cache-cndb`](
        http://confine-project.eu/rel/server/do-cache-cndb)
    
    Endpoint containing the function URI used to cache CNDB description of this node.
    
    POST data: `null`
    """
    url_name = 'cache-cndb'
    
    def get_object(self, pk):
        return get_object_or_404(Node, pk=pk)
    
    def post(self, request, *args, **kwargs):
        if request.DATA is None:
            node = get_object_or_404(Node, pk=kwargs.get('pk'))
            self.check_object_permissions(self.request, node)
            node.cn.cache_node_db()
            response_data = {'detail': 'Node description updated according to CNDB description'}
            return Response(response_data, status=status.HTTP_200_OK)
        raise exceptions.ParseError(detail='This endpoint only accepts null data')


# Monkey patching
insert_ctl(NodeDetail, CacheCNDB)

from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from api import exceptions, generics
from api.utils import insert_ctl
from nodes.api import NodeDetail
from nodes.models import Node
from slices.api import SliverDetail
from slices.models import Sliver

from .serializers import StateSerializer
from .tasks import get_state


class State(generics.RetrieveAPIView):
    """Base State controller view that exposes state information."""
    url_name = 'state'
    rel = 'http://confine-project.eu/rel/controller/state'
    serializer_class = StateSerializer
    model = None # should be defined on subclasses
    
    def __init__(self, *args, **kwargs):
        super(State, self).__init__(*args, **kwargs)
        if self.model is None:
            raise ValueError("You should define 'model' attribute.")
    
    def get(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(self.model, pk=pk)
        serializer = self.get_serializer(obj.state)
        return Response(serializer.data)
    
    def post(self, request, pk, *args, **kwargs):
        """Update state data querying node API."""
        if not request.DATA:
            obj = get_object_or_404(self.model, pk=pk)
            opts = self.model._meta
            module = '%s.%s' % (opts.app_label, opts.object_name)
            get_state.delay(module, ids=[obj.pk], lock=False)
            return self.get(request, pk, *args, **kwargs)
        raise exceptions.ParseError(detail='This endpoint do not accept data')


class NodeState(State):
    model = Node


class SliverState(State):
    model = Sliver


insert_ctl(NodeDetail, NodeState)
insert_ctl(SliverDetail, SliverState)

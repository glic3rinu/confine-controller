from __future__ import absolute_import

from api import generics
from api.utils import insert_ctl
from nodes.api import NodeDetail

from .models import NodeGeolocation
from .serializers import NodeGeolocationSerializer


class Gis(generics.RetrieveUpdateDestroyAPIView):
    url_name = 'gis'
    rel = 'http://confine-project.eu/rel/controller/gis'
    serializer_class = NodeGeolocationSerializer
    model = NodeGeolocation
    list = False


insert_ctl(NodeDetail, Gis)

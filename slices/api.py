from __future__ import absolute_import

from rest_framework import generics

from api import api

from .models import Slice, Sliver, Template
from .serializers import SliceSerializer, SliverSerializer, TemplateSerializer


class SliceList(generics.ListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Slice.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#slice_at_server)
    
    This resource lists the [slices](http://wiki.confine-project.eu/arch:rest-
    api?&#slice_at_server) present in the testbed and provides API URIs to 
    navigate to them.
    """
    model = Slice
    serializer_class = SliceSerializer
    filter_fields = ('set_state', )


class SliceDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Slice.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#slice_at_server)
    
    This resource describes a slice in the testbed, including its [slivers](
    http://wiki.confine-project.eu/arch:rest-api?&#sliver_at_server) with API 
    URIs to navigate to them.
    """
    model = Slice
    serializer_class = SliceSerializer


class SliverList(generics.ListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Sliver.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#sliver_at_server)
    
    This resource lists the  [slivers](http://wiki.confine-project.eu/arch:rest-
    api?&#sliver_at_server) present in the testbed and provides API URIs to 
    navigate to them.
    """
    model = Sliver
    serializer_class = SliverSerializer
    filter_fields = ['slice__name', 'slice__set_state', 'node', 'node__id']


class SliverDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Sliver.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#sliver_at_server)
    
    This resource describes a sliver in the testbed, with API URIs to navigate 
    to the [slice](http://wiki.confine-project.eu/arch:rest-api?&#slice_at_server)
    it is part of and the [node](http://wiki.confine-project.eu/arch:rest-api?
    &#node_at_server) it is intended to run on.
    """
    model = Sliver
    serializer_class = SliverSerializer


class TemplateList(generics.ListCreateAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Template.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#template_at_server)
    
    This resource lists the sliver [templates](http://wiki.confine-project.eu/
    arch:rest-api?&#template_at_server) available in the testbed and provides 
    API URIs to navigate to them.
    """
    model = Template
    serializer_class = TemplateSerializer


class TemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** [`application/vnd.confine.server.Template.v0+json`](http://
    wiki.confine-project.eu/arch:rest-api?&#template_at_server)
    
    This resource describes a template available in the testbed for [slices](
    http://wiki.confine-project.eu/arch:rest-api?&#slice_at_server) and 
    [slivers](http://wiki.confine-project.eu/arch:rest-api?&#sliver_at_server)
    to use.
    """
    model = Template
    serializer_class = TemplateSerializer


api.register(SliceList, SliceDetail)
api.register(SliverList, SliverDetail)
api.register(TemplateList, TemplateDetail)


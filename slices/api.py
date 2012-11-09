from common.api import api
from slices.models import Slice, Sliver, Template
from slices.serializers import SliceSerializer, SliverSerializer, TemplateSerializer
from rest_framework import generics


class SliceList(generics.ListCreateAPIView):
    """
    **Media type:** `application/vnd.confine.server.SliceList.v0+json`
    
    This resource lists the slices present in the testbed and provides API URIs 
    to navigate to them.
    """
    model = Slice
    serializer_class = SliceSerializer
    filter_fields = ('set_state', )


class SliceDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** `application/vnd.confine.server.Slice.v0+json`
    
    This resource describes a slice in the testbed, including its slivers with 
    API URIs to navigate to them.
    """
    model = Slice
    serializer_class = SliceSerializer


class SliverList(generics.ListCreateAPIView):
    """
    **Media type:** `application/vnd.confine.server.SliverList.v0+json`
    
    This resource lists the slivers present in the testbed and provides API URIs 
    to navigate to them.
    """
    
    model = Sliver
    serializer_class = SliverSerializer


class SliverDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** `application/vnd.confine.server.Sliver.v0+json`
    
    This resource describes a sliver in the testbed, with API URIs to navigate 
    to the slice it is part of and the node it is intended to run on.
    """
    model = Sliver
    serializer_class = SliverSerializer


class TemplateList(generics.ListCreateAPIView):
    """
    **Media type:** `application/vnd.confine.server.TemplateList.v0+json`
    
    This resource lists the sliver templates available in the testbed and 
    provides API URIs to navigate to them.
    """
    model = Template
    serializer_class = TemplateSerializer


class TemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    **Media type:** `application/vnd.confine.server.Template.v0+json`
    
    This resource describes a template available in the testbed for slices and 
    slivers to use.
    """
    model = Template
    serializer_class = TemplateSerializer


api.register(SliceList, SliceDetail)
api.register(SliverList, SliverDetail)
api.register(TemplateList, TemplateDetail)


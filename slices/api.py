from apis import rest
from slices.models import Slice, Sliver, Template
from slices.serializers import SliceSerializer, SliverSerializer, TemplateSerializer
from rest_framework import generics

class SliceList(generics.ListCreateAPIView):
    model = Slice
    serializer_class = SliceSerializer


class SliceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Slice
    serializer_class = SliceSerializer


class SliverList(generics.ListCreateAPIView):
    model = Sliver
    serializer_class = SliverSerializer

class SliverDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Sliver
    serializer_class = SliverSerializer


class TemplateList(generics.ListCreateAPIView):
    model = Template


class TemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Template


rest.api.register(SliceList, SliceDetail)
rest.api.register(SliverList, SliverDetail)
rest.api.register(TemplateList, TemplateDetail)


from slices.models import Sliver, Slice, Template
from slices.serializers import SlivererSializer, SliceSerializer, TemplateSerializer
from rest_framework import generics


class Slivers(generics.ListCreateAPIView):
    model = Sliver
    serializer_class = SliverSerializer


class Sliver(generics.RetrieveUpdateDestroyAPIView):
    model = Sliver
    serializer_class = SliverSerializer


from controller import api
from rest_framework import generics
from tinc.models import Island
from tinc.serializers import IslandSerializer


class Islands(generics.ListCreateAPIView):
    model = Island
    serializer_class = IslandSerializer


class Island(generics.RetrieveUpdateDestroyAPIView):
    model = Island
    serializer_class = IslandSerializer


api.register((Islands, Island), 'island')

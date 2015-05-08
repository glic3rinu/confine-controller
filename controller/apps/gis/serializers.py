from __future__ import absolute_import

from controller.apps.api import serializers

from .models import NodeGeolocation

class NodeGeolocationSerializer(serializers.ModelSerializer):
    coordinates = serializers.CharField(source='geolocation')
    lat = serializers.Field()
    lon = serializers.Field()
    
    class Meta:
        model = NodeGeolocation
        fields = ('address', 'coordinates', 'lat', 'lon')

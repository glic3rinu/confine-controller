from rest_framework import serializers
from tinc.models import Island, TincAddress, TincHost, TincClient


class TincHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TincHost


class TincAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = TincAddress
        exclude = ('id',)


class IslandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Island


class TincClientSerializer(serializers.ModelSerializer):
    connect_to = TincAddressSerializer()
    islands = IslandSerializer()
    name = serializers.CharField()
    
    class Meta:
        model = TincClient
        exclude = ('object_id', 'content_type', 'id')

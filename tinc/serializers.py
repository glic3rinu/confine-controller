from rest_framework import serializers
from tinc.models import TincHost, TincClient


class TincHostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TincHost


class TincClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = TincClient

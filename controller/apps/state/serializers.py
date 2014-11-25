from __future__ import absolute_import

from api import serializers

from .models import State


class StateSerializer(serializers.ModelSerializer):
    current = serializers.Field()
    last_change_on = serializers.Field()
    url = serializers.URLField(source='get_url')
    verified = serializers.Field(source='ssl_verified')
    metadata = serializers.JSONField()
    data = serializers.JSONField()
    
    class Meta:
        model = State
        fields = ('current', 'last_change_on', 'last_seen_on', 'url',
                  'verified', 'metadata', 'data')

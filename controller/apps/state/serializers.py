from __future__ import absolute_import

from api import api, serializers

from .models import State


class StateSerializer(serializers.ModelSerializer):
    current = serializers.Field()
    last_change_on = serializers.Field()
    
    class Meta:
        model = State
        fields = ('current', 'last_change_on', 'last_seen_on')

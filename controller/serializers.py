from __future__ import absolute_import

from api import serializers
from controller.models import Testbed, TestbedParams

class TestbedParamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestbedParams
        exclude = ('testbed',)

class TestbedSerializer(serializers.ModelSerializer):
    testbed_params = TestbedParamsSerializer()
    
    class Meta:
        model = Testbed
        exclude = ('id',)

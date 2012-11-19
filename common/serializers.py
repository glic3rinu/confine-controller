from rest_framework import serializers


class UriHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    uri = serializers.HyperlinkedIdentityField()
    
    def __init__(self, *args, **kwargs):
        super(UriHyperlinkedModelSerializer, self).__init__(*args, **kwargs)
        self.fields.pop('url')

from rest_framework import serializers


class UriHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    uri = serializers.HyperlinkedIdentityField()
    
    def __init__(self, *args, **kwargs):
        super(UriHyperlinkedModelSerializer, self).__init__(*args, **kwargs)
        self.fields.pop('url')


class HyperlinkedFileField(serializers.FileField):
    def to_native(self, value):
        if value:
            request = self.context.get('request', None)
            return request.build_absolute_uri(value.url)


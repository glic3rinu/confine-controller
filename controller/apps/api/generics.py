from rest_framework import generics

from .serializers import UriHyperlinkedModelSerializer


class URIListCreateAPIView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'GET' and not hasattr(self, 'response'):
            class DefaultSerializer(UriHyperlinkedModelSerializer):
                class Meta:
                    model = self.model
                    fields = ['uri']
            return DefaultSerializer
        return super(URIListCreateAPIView, self).get_serializer_class()

from django.utils.encoding import force_unicode
from rest_framework import generics
from rest_framework.generics import *

from . import serializers
from .utils import link_header


class URIListCreateAPIView(ListCreateAPIView):
    def get_serializer_class(self):
        # TODO until the partial response is not implemented we'll serve full resources
#        if self.request.method == 'GET' and not hasattr(self, 'response'):
#            class DefaultSerializer(serializers.UriHyperlinkedModelSerializer):
#                class Meta:
#                    model = self.model
#                    fields = ['uri']
#            return DefaultSerializer
        return super(URIListCreateAPIView, self).get_serializer_class()
    
    def get(self, request, *args, **kwargs):
        """ Add link header """
        response = super(URIListCreateAPIView, self).get(request, *args, **kwargs)
        response['Link'] = link_header(['base'], request)
        return response



class RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    def get(self, request, *args, **kwargs):
        """ Add link header """
        response = super(RetrieveUpdateDestroyAPIView, self).get(request, *args, **kwargs)
        name = force_unicode(self.model._meta.verbose_name)
        response['Link'] = link_header(['base', '%s-list' % name], request)
        return response
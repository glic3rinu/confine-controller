from django.utils.encoding import force_unicode
from rest_framework import generics
from rest_framework.generics import *

from controller.models.utils import is_singleton

from .serializers import DynamicReadonlyFieldsModelSerializer
from .utils import link_header


class URIListCreateAPIView(ListCreateAPIView):
    """
    Used for read-write endpotins to represent a collection of
    model instances. Provides get and post method handlers and
    has link to API base.
    `add_serializer_class` allows to use a different serializer
    on object creation (POST).
    
    """
    add_serializer_class = None # Serializer used on object creation
    def get_serializer_class(self):
        # TODO until the partial response is not implemented we'll serve full resources
#        if self.request.method == 'GET' and not hasattr(self, 'response'):
#            class DefaultSerializer(serializers.UriHyperlinkedModelSerializer):
#                class Meta:
#                    model = self.model
#                    fields = ['uri']
#            return DefaultSerializer
        if self.request.method == 'POST' and self.add_serializer_class:
            return self.add_serializer_class
        return super(URIListCreateAPIView, self).get_serializer_class()
    
    def get(self, request, *args, **kwargs):
        """ Add link header """
        response = super(URIListCreateAPIView, self).get(request, *args, **kwargs)
        base_link = ('base', 'http://confine-project.eu/rel/server/base')
        response['Link'] = link_header([base_link], request)
        return response
    
    def get_success_headers(self, data):
        try:
            return {'Location': data['uri']}
        except (TypeError, KeyError):
            return {}



class RetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Used for read-write-delete endpoints to represent a single model instance.
    Provides get, put, patch and delete method handlers.
    Adds links to the API base and controller API endpoints.
    `fields_superuser` allows defining fields that only can be updated
    by a superuser (mark they as readonly otherwise).
    NOTE: Serializer should be a subclass of DynamicReadonlyFieldsModelSerializer
    
    """
    fields_superuser = [] # Fields that only superusers can update
    
    def get(self, request, *args, **kwargs):
        """ Add link header """
        response = super(RetrieveUpdateDestroyAPIView, self).get(request, *args, **kwargs)
        name = force_unicode(self.model._meta.verbose_name)
        links = [('base', 'http://confine-project.eu/rel/server/base')]
        if not is_singleton(self.model) and getattr(self, 'list', True):
            resource = '%s-list' % name
            link = (resource, 'http://confine-project.eu/rel/server/%s' % resource)
            links.append(link)
        object_id = kwargs.get('pk')
        for endpoint in getattr(self, 'ctl', []):
            resource = '%s-ctl-%s' % (name, endpoint.url_name)
            links.append((resource, endpoint.rel, object_id))
        response['Link'] = link_header(links, request)
        return response
    
    def get_serializer(self, instance=None, data=None,
                       files=None, many=False, partial=False):
        """ Mark as readonly fields that only can be updated by superusers """
        if (self.request.method in ['PUT' or 'PATCH'] and
            not self.request.user.is_superuser and self.fields_superuser):
            serializer_class = self.get_serializer_class()
            assert issubclass(serializer_class, DynamicReadonlyFieldsModelSerializer),\
                "Serializer %s should be a subclass of %s" % (serializer_class,
                DynamicReadonlyFieldsModelSerializer)
            return serializer_class(instance=instance, data=data, files=files,
                    many=many, read_only_fields=self.fields_superuser)
        
        return super(RetrieveUpdateDestroyAPIView, self).get_serializer(
            instance=instance, data=data, files=files, many=many, partial=partial)


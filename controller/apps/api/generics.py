from django.conf import settings
from rest_framework import generics
from rest_framework.generics import *
from rest_framework.renderers import BrowsableAPIRenderer

from controller.models.utils import is_singleton

from . import ApiRoot
from .helpers import build_pagination_link, model_name_urlize
from .renderers import ResourceListJSONRenderer
from .serializers import DynamicReadonlyFieldsModelSerializer
from .utils import link_header


class ControllerBase(object):
    """
    Controller base class for all other generic views.
    """
    controller_view = False # registry or controller view
    
    @property
    def _rel_prefix(self):
        if self.controller_view:
            return ApiRoot.CONTROLLER_REL_PREFIX
        return ApiRoot.REGISTRY_REL_PREFIX


class URIListCreateAPIView(ControllerBase, generics.ListCreateAPIView):
    """
    Used for read-write endpotins to represent a collection of
    model instances. Provides get and post method handlers and
    has link to API base.
    `add_serializer_class` allows to use a different serializer
    on object creation (POST).
    
    """
    add_serializer_class = None # Serializer used on object creation
    renderer_classes = [ResourceListJSONRenderer, BrowsableAPIRenderer]
    
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
        """ Add link header and pagination links."""
        response = super(URIListCreateAPIView, self).get(request, *args, **kwargs)
        base_link = [
            ('base', ApiRoot.REGISTRY_REL_PREFIX + 'base'),
            ('base_controller', ApiRoot.CONTROLLER_REL_PREFIX + 'base'),
        ]
        base_links = link_header(base_link, request)
        
        # generate pagination links
        pagination_links = [
            build_pagination_link(request, 'first', '1'),
            build_pagination_link(request, 'last', self.last_page),
            build_pagination_link(request, 'prev', self.prev_page),
            build_pagination_link(request, 'next', self.next_page),
        ]
        pagination_links = [link for link in pagination_links if link is not None]
        response['Link'] =  base_links + ', ' + ', '.join(pagination_links)
        return response
    
    def get_queryset(self):
        """
        Return a queryset based on pagination:
        http://wiki.confine-project.eu/arch:rest-api#pagination
        """
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        qs = super(URIListCreateAPIView, self).get_queryset()
        per_page = self.request.GET.get('per_page')
        num_page = self.request.GET.get('page')
        
        # validate per_page
        try:
            per_page = int(per_page)
        except (ValueError, TypeError):
            per_page = settings.DEFAULT_PER_PAGE
        else:
            # per_page cannot be less than 1
            per_page = max(1, per_page)
        
        # Is pagination disabled?
        if per_page is None:
            per_page = max(1, qs.count())
        paginator = Paginator(qs, per_page)
        
        # validate num_page
        try:
            page = paginator.page(num_page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page = paginator.page(paginator.num_pages)
        
        # store pagination to create link headers: first, last, prev, next.
        self.last_page = page.paginator.num_pages
        self.prev_page = page.previous_page_number() if page.has_previous() else None
        self.next_page = page.next_page_number() if page.has_next() else None
        
        # filter against queryset because a queryset is required by filtering.
        # FIXME find a more clean and efficient approach.
        ids = [obj.pk for obj in page.object_list]
        return qs.filter(pk__in=ids)
    
    def get_success_headers(self, data):
        try:
            return {'Location': data['uri']}
        except (TypeError, KeyError):
            return {}



class RetrieveUpdateDestroyAPIView(ControllerBase, generics.RetrieveUpdateDestroyAPIView):
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
        name = model_name_urlize(self.model)
        links = [
            ('base', ApiRoot.REGISTRY_REL_PREFIX + 'base'),
            ('base_controller', ApiRoot.CONTROLLER_REL_PREFIX + 'base'),
        ]
        if not is_singleton(self.model) and getattr(self, 'list', True):
            resource = '%s-list' % name
            link = (resource, self._rel_prefix + resource)
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


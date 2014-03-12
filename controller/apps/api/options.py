from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import patterns, url
from django.utils import six
from django.utils.encoding import force_unicode
from django.utils.importlib import import_module
from rest_framework.views import APIView
from rest_framework.response import Response

from controller.models.utils import is_singleton
from controller.utils import autodiscover

from .utils import link_header


class ApiRoot(APIView):
    """ 
    This is the entry point for the REST API.
    
    Follow the hyperinks each resource offers to explore the API.
    
    Note that you can also explore the API from the command line, for instance 
    using the curl command-line tool.
    
    For example: `curl -X GET https://your_domain.net/api/ 
    -H "Accept: application/json; indent=4"`
    """
    def get(base_view, request, format=None):
        relations = [
            ('base', 'http://confine-project.eu/rel/server/base'),
            ('api-token-auth', 'http://confine-project.eu/rel/controller/do-get-auth-token')
        ]
        # http://confine-project.eu/rel/server like resources
        for model in api._registry:
            name = force_unicode(model._meta.verbose_name)
            name = name if is_singleton(model) else '%s-list' % name
            rel = 'http://confine-project.eu/rel/server/%s' % name
            relations.append((name, rel))
        headers = {'Link': link_header(relations, request)}
        return Response({}, headers=headers)


class RestApi(object):
    def __init__(self):
        self._registry = {}
    
    def register(self, *args):
        model = args[0].model
        self._registry.update({model: args})
    
    def base(self):
        api_root = getattr(settings, 'CUSTOM_API_ROOT', 'api.ApiRoot')
        mod, inst = api_root.rsplit('.', 1)
        mod = import_module(mod)
        api_root = getattr(mod, inst)
        return api_root.as_view()
    
    @property
    def urls(self):
        return self.get_urls()
    
    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.base(), name='base'),)
        
        for model, resource in six.iteritems(self._registry):
            name = force_unicode(model._meta.verbose_name)
            name_plural = force_unicode(model._meta.verbose_name_plural)
            list_view, detail_view = resource
            for endpoint in getattr(detail_view, 'ctl', []):
                urlpatterns += patterns('',
                    url(r'^%s/(?P<pk>[0-9]+)/ctl/%s/$' % (name_plural, endpoint.url_name),
                        endpoint.as_view(),
                        name="%s-ctl-%s" % (name, endpoint.url_name)),
                )
            urlpatterns += patterns('',
                url(r'^%s/$' % name_plural,
                    list_view.as_view(),
                    name=name if is_singleton(model) else '%s-list' % name),
                url(r'^%s/(?P<pk>[0-9]+)$' % name_plural,
                    detail_view.as_view(),
                    name="%s-detail" % name),
            )

        return urlpatterns
    
    def autodiscover(self):
        """ Auto-discover api.py and serializers.py modules """
        autodiscover('api')
        autodiscover('serializers')
    
    def aggregate(self, model, field, name, **kwargs):
        """ Dynamically add new fields to an existing serializer """
        # TODO provide support for hooking with nested serializers
        if model in self._registry:
            model_serializers = []
            for api_view in self._registry[model]:
                model_serializers.append(api_view.serializer_class)
                # include serializers used on object creation
                if getattr(api_view, 'add_serializer_class', None):
                    model_serializers.append(api_view.add_serializer_class)
            
            # hook new attribute to each serializer
            for serializer in model_serializers:
                serializer.base_fields.update({name: field(**kwargs)})


# singleton
api = RestApi()


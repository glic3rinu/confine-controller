from __future__ import absolute_import

from django.conf import settings
from django.conf.urls import patterns, url
from django.utils.importlib import import_module
from rest_framework.views import APIView
from rest_framework.response import Response

from controller.models.utils import is_singleton
from controller.utils import autodiscover

from .helpers import get_registry_urls, model_name_urlize
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
    CONFINE_REL_PREFIX = 'http://confine-project.eu/rel/'
    REGISTRY_REL_PREFIX = CONFINE_REL_PREFIX + 'registry/'
    CONTROLLER_REL_PREFIX = CONFINE_REL_PREFIX + 'controller/'
    
    def get(base_view, request, format=None):
        relations = [
            ('base', ApiRoot.REGISTRY_REL_PREFIX + 'base'),
            ('api-token-auth', ApiRoot.CONTROLLER_REL_PREFIX + 'do-get-auth-token')
        ]
        # http://confine-project.eu/rel/server like resources
        for model in api._registry:
            name = model_name_urlize(model)
            name = name if is_singleton(model) else '%s-list' % name
            rel = ApiRoot.REGISTRY_REL_PREFIX + name
            relations.append((name, rel))
        
        # backwards compatibility rel links #236
        relations.append(('server', ApiRoot.REGISTRY_REL_PREFIX + 'server'))
        
        # http://confine-project.eu/rel/controller like resources
        for model in api._registry_controller:
            name = model_name_urlize(model)
            name = name if is_singleton(model) else '%s-list' % name
            rel = ApiRoot.CONTROLLER_REL_PREFIX + name
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
        
        return urlpatterns + get_registry_urls(self._registry)
    
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
        else:
            import warnings
            warnings.warn("Model %s not registered, so api.aggregate do nothing." % model)



class ControllerRestApi(RestApi):
    """Provide controller functionallities to RestApi"""
    def __init__(self):
        super(ControllerRestApi, self).__init__()
        self._registry_controller = {}
    
    def register(self, *args):
        controller_view = args[0].controller_view
        if controller_view:
            model = args[0].model
            self._registry_controller.update({model: args})
        else:
            super(ControllerRestApi, self).register(*args)
    
    def get_urls(self):
        urlpatterns = super(ControllerRestApi, self).get_urls()
        urlpatterns += patterns('',
            url(r'^$', self.base(), name='base_controller'),)
        return urlpatterns + get_registry_urls(self._registry_controller)

# singleton
api = ControllerRestApi()


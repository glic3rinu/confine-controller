from django.conf import settings
from django.conf.urls import patterns, url
from django.utils import six
from django.utils.encoding import smart_str, force_unicode
from django.utils.importlib import import_module
from nodes import settings as nodes_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse


# TODO Reimplement resource with rest_framework.ModelResource and urls with Routers
#      when they become available in the final release of rest_framework2
# TODO Make this more generic, for now only works with Model based resources


class RestApi(object):
    def __init__(self):
        self._registry = {}
    
    def register(self, *args):
        model = args[0].model
        self._registry.update({model: args})
    
    def base(self):
        # TODO Move definition to controller/api.py ?
        class Base(APIView):
            """ 
            **Media type:** `application/vnd.confine.server.Base.v0+json`
            
            This resource is located at the base URI of the server API. It 
            describes testbed-wide parameters and provides the API URIs to 
            navigate to other resources in the testbed.
            """
            def get(base_view, request, format=None):
                testbed_params = {
                    "mgmt_ipv6_prefix": nodes_settings.MGMT_IPV6_PREFIX,
                    "priv_ipv4_prefix_dflt": nodes_settings.PRIV_IPV4_PREFIX_DFLT,
                    "sliver_mac_prefix_dflt": nodes_settings.SLIVER_MAC_PREFIX_DFLT, }
                
                output = {"testbed_params": testbed_params}
                for model in self._registry:
                    name = force_unicode(model._meta.verbose_name)
                    name_plural = force_unicode(model._meta.verbose_name_plural)
                    output.update({'%s_href' % name_plural: reverse('%s-list' % name,
                        args=[], request=request)})
                return Response(output)
        
        return Base.as_view()
    
    @property
    def urls(self):
        return self.get_urls()
    
    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.base(), name='base'),)
        
        for model, resource in six.iteritems(self._registry):
            # TODO Support for nested resources on urls /api/nodes/1111/ctl
            name = force_unicode(model._meta.verbose_name)
            name_plural = force_unicode(model._meta.verbose_name_plural)
            urlpatterns += patterns('',
                url(r'^%s/$' % name_plural,
                    resource[0].as_view(),
                    name='%s-list' % name),
                url(r'^%s/(?P<pk>[0-9]+)$' % name_plural, 
                    resource[1].as_view(),
                    name="%s-detail" % name),
            )
        return urlpatterns
    
    def autodiscover(self):
        """ Auto-discover INSTALLED_APPS api.py modules """
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            try: import_module('%s.api' % app)
            except ImportError: pass
    
    def aggregate(self, model, field, name):
        """ Dynamically add new fields to an existing serializer """
        # TODO provide support for hooking with nested serializers
        if model in self._registry:
            self._registry[model][0].serializer_class.base_fields.update({name: field()})
            self._registry[model][1].serializer_class.base_fields.update({name: field()})

# singleton
api = RestApi()


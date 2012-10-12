from django.conf import settings
from django.conf.urls import patterns, url
from django.utils import six
from django.utils.importlib import import_module
from nodes import settings as nodes_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse


# TODO improvements on autodiscoverability of resource_name and more


class Api(object):
    def __init__(self):
        self._registry = {}
    
    def register(self, resource, name):
        self._registry.update({name: resource})

    def base(self):
        class Base(APIView):
            """ 
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
                for name in self._registry:
                    output.update({'%s_href' % name: reverse('%s-list' %name, 
                                                             args=[], 
                                                             request=request)})
                return Response(output)

        return Base.as_view()

    @property
    def urls(self):
        # This is ugly, but don't know why don't work without it
        class FakeModule(object):
            urlpatterns = self.get_urls()
        return FakeModule()

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.base(), name='base'),)

        for resource_name, (resource_list, resource) in six.iteritems(self._registry):
            urlpatterns += patterns('',
                url(r'^%ss/' % resource_name, 
                    resource_list.as_view(),
                    name='%s-list' % resource_name),
                url(r'^%ss/(?P<pk>[0-9]+)$' % resource_name, 
                    resource.as_view(),
                    name="%s-detail" % resource_name),
            )
        return urlpatterns

    def autodiscover(self):
        """ Auto-discover INSTALLED_APPS api.py modules """
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            try: import_module('%s.api' % app)
            except ImportError: pass

# singletons
api = Api()


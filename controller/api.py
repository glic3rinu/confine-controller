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
# TODO make this reusable within their own application: maybe this app should 
#      be called apis and have a rest module to avoid module clashing

class Api(object):
    def __init__(self):
        self._registry = {}
    
    def register(self, resource):
        self._registry.update({resource[0].model: resource})

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
                for model in self._registry:
                    name = force_unicode(model._meta.verbose_name)
                    name_plural = force_unicode(model._meta.verbose_name_plural)
                    output.update({'%s_href' % name_plural: reverse('%s-list' % name,
                        args=[], request=request)})
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

        for model, resource in six.iteritems(self._registry):
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
    
    def insert_field(self, model, field):
        for resource in self._registry[model]:
            resource.serializer_class.tinc = field

# singletons
api = Api()


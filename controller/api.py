from controller.views import Base
from django.conf import settings
from django.conf.urls import patterns, url
from django.utils import six
from django.utils.importlib import import_module


class Api(object):
    def __init__(self):
        self._registry = {}
    
    def register(self, resource, name):
        self._registry.update({name: resource})

    def base(self):
        return Base.as_view()

    @property
    def urls(self):
        return self.get_urls(), 'controller', 'controller'

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

api = Api()




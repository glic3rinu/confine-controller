from django.conf.urls import patterns, url
from nodes.views import NodeRoot, NodeInstance, APIRootView


urlpatterns = patterns('nodes.views',
    url(r'^$', NodeRoot.as_view()),
    url(r'^(?P<pk>[0-9]+)$', NodeInstance.as_view(), name="node_instance"),
    )


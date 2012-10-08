from django.conf.urls import patterns, url
from nodes.resources import NodeRoot, NodeInstance


urlpatterns = patterns('nodes.views',
    url(r'^$', NodeRoot.as_view()),
    url(r'^(?P<pk>[0-9]+)$', NodeInstance.as_view())
)


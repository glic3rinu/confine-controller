from django.conf.urls import patterns, url
from nodes.views import Nodes, Node
from nodes.resources import NodeResource

node_root = NodeResource.as_view(actions={
    'get': 'list',
    'post': 'create'
})

node_instance = NodeResource.as_view(actions={
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})


urlpatterns = patterns('nodes.views',
    url(r'^$', Nodes.as_view(), name='nodes'),
    url(r'^(?P<pk>[0-9]+)$', Node.as_view(), name="node"),
    url(r'^rata$', node_root),
    url(r'^rata/(?P<pk>[0-9]+)$', node_instance),
    )


from django.conf.urls import patterns, url
from nodes.views import Nodes, Node

urlpatterns = patterns('nodes.views',
    url(r'^$', Nodes.as_view(), name='nodes'),
    url(r'^(?P<pk>[0-9]+)$', Node.as_view(), name="node"),
    )


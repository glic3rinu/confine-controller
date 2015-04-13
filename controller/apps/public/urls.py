from django.conf.urls import patterns, url

from .views import NodeSliverDetailView, NodeSliverListView


urlpatterns = patterns('',
    url("^nodes/(?P<object_id>\d+)/slivers/$",
        NodeSliverListView.as_view(),
        name='public_node_sliver_list'),
    url("^slivers/(?P<object_id>\d+)/$",
        NodeSliverDetailView.as_view(),
        name='public_sliver_detail'),
)

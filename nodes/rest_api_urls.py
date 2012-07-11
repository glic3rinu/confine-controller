from django.conf.urls import patterns, include, url
from nodes import rest_views
urlpatterns = patterns('',
                       url(r'^$',
                           rest_views.testbed,
                           name="rest_testbed"),
                       url(r'^nodes/$',
                           rest_views.node_list,
                           name="rest_node_list"),
                       url(r'^nodes/([0-9]+)/$',
                           rest_views.node,
                           name="rest_node"),
                       )

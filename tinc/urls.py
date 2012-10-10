from django.conf.urls import patterns, url
from tinc.views import Islands, Island


urlpatterns = patterns('nodes.views',
    url(r'^$', Islands.as_view(), name='island-list'),
    url(r'^(?P<pk>[0-9]+)$', Island.as_view(), name="island-detail"),
    )


from auth_extension.views import UserRoot, UserInstance
from django.conf.urls import patterns, url


urlpatterns = patterns('nodes.views',
    url(r'^$', UserRoot.as_view(), name='user-list'),
    url(r'^(?P<pk>[0-9]+)$', UserInstance.as_view(), name='user-detail')
)


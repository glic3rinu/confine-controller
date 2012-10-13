from apis import rest
from django.contrib import admin
from django.conf.urls import patterns, include, url

admin.autodiscover()
rest.api.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(rest.api.urls)),
)

from common.api import api
from django.contrib import admin
from django.conf.urls import patterns, include, url

admin.autodiscover()
api.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^private/', include('private_files.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(api.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
)

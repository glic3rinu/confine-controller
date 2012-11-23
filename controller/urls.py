from common.api import api
from django.contrib import admin
from django.conf.urls import patterns, include, url

admin.autodiscover()
api.autodiscover()

urlpatterns = patterns('',
    url(r'^confine/admin/', include(admin.site.urls)),
    url(r'^confine/admin_tools/', include('admin_tools.urls')),
    url(r'^confine/private/', include('private_files.urls')),
    url(r'^confine/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^confine/api/', include(api.urls)),
)

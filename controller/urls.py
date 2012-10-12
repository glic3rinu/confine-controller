from controller import api
from django.contrib import admin
from django.conf.urls import patterns, include, url

admin.autodiscover()
api.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^api/', include(api.urls)),
)

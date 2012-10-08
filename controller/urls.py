from controller.views import Base
from django.contrib import admin
from django.conf.urls import patterns, include, url

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^confine/$', Base.as_view()),
    url(r'^confine/nodes/', include('nodes.urls')),
)

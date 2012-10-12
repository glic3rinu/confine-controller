from controller.views import Base
from django.contrib import admin
from django.conf.urls import patterns, include, url

admin.autodiscover()
#api.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
#    url(r'^api/', include(api.urls)),
    url(r'^api/$', Base.as_view()),
    url(r'^api/nodes/', include('nodes.urls')),
    url(r'^api/users/', include('auth_extension.urls')),
    url(r'^api/islands/', include('tinc.urls')),
)

from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from nodes.urls import urlpatterns as nodes_urlpatterns
from user_management.urls import urlpatterns as user_management_urlpatterns

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'confine.views.home', name='home'),
    # url(r'^confine/', include('confine.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^admin_tools/', include('admin_tools.urls')),
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

urlpatterns += nodes_urlpatterns
urlpatterns += user_management_urlpatterns

from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from nodes import views as node_views

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

                       url(r'^$',
                           node_views.index,
                           name="index"),
                       url(r'^node_index/$',
                           node_views.node_index,
                           name="node_index"),
                       url(r'^create_slice/$',
                           node_views.create_slice,
                           name="create_slice"),
                       url(r'^show_own_slices/$',
                           node_views.show_own_slices,
                           name="show_own_slices"),

                       url(r'^upload_node/$',
                           node_views.upload_node,
                           name="upload_node"),
                           
)

from __future__ import absolute_import

from django.contrib import admin
from django.conf.urls import patterns, include, url

from controller.utils import is_installed


admin.autodiscover()


urlpatterns = patterns('',
    # Password reset
    url(r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^reset/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^private/', include('private_files.urls')),
)


if is_installed('registration'):
    urlpatterns += patterns('',
        url(r'^accounts/', include('users.registration.urls')),)
        
if is_installed('captcha'):
    urlpatterns += patterns('',
        url(r'^captcha/', include('captcha.urls')),
    )

if is_installed('api'):
    from api import api
    api.autodiscover()
    
    urlpatterns += patterns('',
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        url(r'^api-token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
        url(r'^api/', include(api.urls)),)


if is_installed('gis'):
    urlpatterns += patterns('',
        url(r'^gis/', include('gis.urls')),)

from django.conf.urls import patterns, url


urlpatterns = patterns('privatefiles.views',
    url(r'^(.+)/(.+)/(.+)/(.+)/(.+)$', 'get_file', name = 'privatefiles-file'),
)

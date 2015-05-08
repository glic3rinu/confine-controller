from django.conf.urls import patterns, url


urlpatterns = patterns('controller.apps.privatefiles.views',
    url(r'^(.+)/(.+)/(.+)/(.+)/(.+)$', 'get_file', name = 'privatefiles-file'),
)

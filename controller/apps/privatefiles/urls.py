from django.conf.urls import patterns, url


urlpatterns = patterns('private_files.views',
    url(r'^(.+)/(.+)/(.+)/(.+)/(.+)$', 'get_file', name = 'private_files-file'),
)

import urllib
import urlparse

from django.conf.urls import patterns, url
from django.utils import six
from django.utils.encoding import force_unicode

from controller.models.utils import is_singleton


def model_name_urlize(model, plural=False):
    """Convert model verbose_name into a url friendly string."""
    name = model._meta.verbose_name_plural if plural else model._meta.verbose_name
    name = force_unicode(name).replace(' ', '')
    return name

def get_registry_urls(registry):
    urlpatterns = patterns('')
    
    for model, resource in six.iteritems(registry):
        name = model_name_urlize(model)
        name_plural = model_name_urlize(model, plural=True)
        list_view, detail_view = resource
        for endpoint in getattr(detail_view, 'ctl', []):
            urlpatterns += patterns('',
                url(r'^%s/(?P<pk>[0-9]+)/ctl/%s/$' % (name_plural, endpoint.url_name),
                    endpoint.as_view(),
                    name="%s-ctl-%s" % (name, endpoint.url_name)),
            )
        urlpatterns += patterns('',
            url(r'^%s/$' % name_plural,
                list_view.as_view(),
                name=name if is_singleton(model) else '%s-list' % name),
            url(r'^%s/(?P<pk>[0-9]+)/$' % name_plural,
                detail_view.as_view(),
                name="%s-detail" % name),
            # backwards compatibility #617 (without final slash)
            url(r'^%s/(?P<pk>[0-9]+)$' % name_plural,
                detail_view.as_view(),
                name="%s-detail" % name),
        )
    
    # backwards compatibility rel links #236
    from nodes.api import ServerDefaultDetail
    urlpatterns += patterns('',
        url(r'^server/$',
            ServerDefaultDetail.as_view(),
            name="server"),
    )
    
    return urlpatterns

def build_pagination_link(request, rel, page):
    if page is None:
        return
    url = urlparse.urlparse(request.get_full_path())
    query = dict(urlparse.parse_qsl(url.query))
    query['page'] = page
    query = urllib.urlencode(query)
    url = request.build_absolute_uri(url.path + '?' + query)
    return '<%s>; rel="%s"' % (url, rel)

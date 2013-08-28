from django.utils.safestring import mark_safe
from rest_framework.reverse import reverse

from .settings import API_REL_BASE_URL


def reverse_rel(relation):
    return API_REL_BASE_URL + relation


def link_header(relations, request):
    links = []
    for rel in relations:
        args = []
        if isinstance(rel, tuple):
            rel, pk = rel
            args = [pk]
        url = reverse(rel, args=args or [], request=request)
        if args:
            rel = 'do-%s' % url.split('/')[-2]
        links.append('<%s>; rel="%s"' % (url, reverse_rel(rel)))
    return ', '.join(links)


def insert_ctl(detail_class, clt_class):
    if hasattr(detail_class, 'ctl'):
        detail_class.ctl.append(clt_class)
    else:
        detail_class.ctl = [clt_class]

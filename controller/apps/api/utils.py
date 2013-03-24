from rest_framework.reverse import reverse
from api.settings import API_REL_BASE_URL
from django.utils.safestring import mark_safe


def reverse_rel(relation):
    return API_REL_BASE_URL + relation


def link_header(relations, request):
    links = []
    for rel in relations:
        args = []
        if type(rel) is tuple:
            rel, pk = rel
            args = [pk]
        url = reverse(rel, args=args or [], request=request)
        links.append('<%s> ; rel="%s"' % (url, reverse_rel(rel)))
    return ', '.join(links)

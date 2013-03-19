from rest_framework.reverse import reverse
from api.settings import API_REL_BASE_URL


def reverse_rel(relation):
    return API_REL_BASE_URL + relation

def link_header(relations, request):
    links = [ '<%s >; rel="%s"' % (reverse(rel, request=request), reverse_rel(rel)) for rel in relations ]
    return ', '.join(links)

from rest_framework.reverse import reverse


def link_header(relations, request):
    links = []
    for rel in relations:
        if len(rel) == 3:
            url_name, rel, args = rel
            args = [args]
        else:
            url_name, rel = rel
            args = []
        url = reverse(url_name, args=args, request=request)
        links.append('<%s>; rel="%s"' % (url, rel))
    return ', '.join(links)


def insert_ctl(detail_class, clt_class):
    if hasattr(detail_class, 'ctl'):
        detail_class.ctl.append(clt_class)
    else:
        detail_class.ctl = [clt_class]

import re

from django.utils.safestring import mark_safe


ESCAPE_MARKS = (('"', '"'), ('<', '>'), ('&lt;', '&gt;'), ('&quot;', '&quot;'))


def urlize(text):
    for ini, end in ESCAPE_MARKS:
        for url in re.findall("%shttp(.*?)%s" % (ini, end), text):
            url = 'http' + url
            link = '%s<a href="%s">%s</a>%s' % (ini, url, url, end)
            url = ini + url + end
            text = text.replace(url, link)
    return text


MONOSPACE_FONTS = ('Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,'
                   'Bitstream Vera Sans Mono,Courier New,monospace')


def monospace_format(text):
    style="font-family:%s;" % MONOSPACE_FONTS
    return mark_safe('<span style="%s">%s</span>' % (style, text))

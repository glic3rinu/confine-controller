import re


ESCAPE_MARKS = (('"', '"'), ('<', '>'), ('&lt;', '&gt;'), ('&quot;', '&quot;'))


def urlize(text):
    for ini, end in ESCAPE_MARKS:
        for url in re.findall("%shttp(.*?)%s" % (ini, end), text):
            url = 'http' + url
            link = '%s<a href="%s">%s</a>%s' % (ini, url, url, end)
            url = ini + url + end
            text = text.replace(url, link)
    return text


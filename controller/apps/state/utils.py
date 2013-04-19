import re


def urlize_escaped_html(text):
    """ Urlizes escaped HTML text """
    for url in re.findall('&quot;http(.*)&quot;', text): # urlize
        link = '&quot;<a href="http%s" rel="nofollow">http%s</a>&quot;' % (url, url)
        url = '&quot;http%s&quot;' % url
        text = text.replace(url, link)
    return text

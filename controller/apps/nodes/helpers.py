from IPy import IP
from urlparse import urlparse


def url_on_mgmt_net(url, addr):
    """Check if url refers management network address."""
    # parse url and try to convert to IP address
    url_netloc = urlparse(url).netloc.strip('[]')
    try:
        url_ip = IP(url_netloc)
    except ValueError:
        return False
    return addr == url_ip

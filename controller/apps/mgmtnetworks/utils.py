from django.contrib.contenttypes.models import ContentType
from IPy import IP

from controller import settings

from mgmtnetworks.tinc.models import TincClient, TincServer, Gateway


def reverse(ip):
    """ Reverse IP resolution """
    if type(ip) in [str, unicode]:
        ip = IP(ip)
    if ip.version() == 6:
        ip_words = ip.strFullsize().split(':')
        prefix = settings.MGMT_IPV6_PREFIX.split(':')[:3]
        prefix = [ word.zfill(4) for word in prefix ]
        if ip_words[:3] != prefix:
            return None
        if ip_words[4] == '0000' and ip_words[-1] == '0002':
            # MGMT_IPV6_PREFIX:N:0000::2/64 i
            ct = ContentType.objects.get(app_label='nodes', model='node')
            node_id = int(ip_words[3], 16)
            return TincClient.objects.get(object_id=node_id,
                content_type=ct).content_object
        elif ip_words[3] == '0000' and ip_words[4] == '2000':
            # MGMT_IPV6_PREFIX:0:2000:hhhh:hhhh:hhhh/128
            ct = ContentType.objects.get(app_label='tinc', model='host')
            host_id = int(''.join(ip_words[5:]), 16)
            return TincClient.objects.get(object_id=host_id,
                content_type=ct).content_object
        elif ip_words[3] == '0000' and ip_words[4] == '0000':
            # MGMT_IPV6_PREFIX:0:0000::2/128
            ct = ContentType.objects.get(app_label='nodes', model='server')
            return TincServer.objects.get(content_type=ct).content_object
        elif ip_words[3] == '0000' and ip_words[4] == '0001':
            # MGMT_IPV6_PREFIX:0:0001:gggg:gggg:gggg/128
            ct = ContentType.objects.get(app_label='tinc', model='gateway')
            gateway_id = int(''.join(ip_words[5:]), 16)
            return TincServer.objects.get(object_id=gateway_id,
                content_type=ct).content_object
    return None

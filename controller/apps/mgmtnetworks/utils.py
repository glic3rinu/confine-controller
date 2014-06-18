from django.contrib.contenttypes.models import ContentType
from IPy import IP

from controller import settings
from controller.core.exceptions import InvalidMgmtAddress


def reverse(ip):
    """ Reverse IP resolution """
    if type(ip) in [str, unicode]:
        try:
            ip = IP(ip)
        except ValueError:
            raise InvalidMgmtAddress('%s is not a valid IP address' % ip)
    if ip.version() == 6:
        ip_words = ip.strFullsize().split(':')
        prefix = settings.MGMT_IPV6_PREFIX.split(':')[:3]
        prefix = [ word.zfill(4) for word in prefix ]
        client_type = False
        if ip_words[:3] != prefix:
            raise InvalidMgmtAddress('%s is not a valid mgmt address' % ip)
        if ip_words[4] == '0000' and ip_words[-1] == '0002':
            # MGMT_IPV6_PREFIX:N:0000::2/64 i
            ct = ContentType.objects.get(app_label='nodes', model='node')
            object_id = int(ip_words[3], 16)
        elif ip_words[3] == '0000' and ip_words[4] == '2000':
            # MGMT_IPV6_PREFIX:0:2000:hhhh:hhhh:hhhh/128
            ct = ContentType.objects.get(app_label='tinc', model='host')
            object_id = int(''.join(ip_words[5:]), 16)
        elif ip_words[3] == '0000' and ip_words[4] == '0000':
            # MGMT_IPV6_PREFIX:0:0000::2/128
            ct = ContentType.objects.get(app_label='nodes', model='server')
            object_id = 1
        elif ip_words[3] == '0000' and ip_words[4] == '0001':
            # MGMT_IPV6_PREFIX:0:0001:gggg:gggg:gggg/128
            ct = ContentType.objects.get(app_label='tinc', model='gateway')
            object_id = int(''.join(ip_words[5:]), 16)
        try:
            client = ct.get_object_for_this_type(id=object_id)
        except ct.model_class().DoesNotExist:
            raise InvalidMgmtAddress('No object related with %s mgmt IP' % ip)
        return client
    raise InvalidMgmtAddress('%s is not a valid mgmt address' % ip)

from django.core.exceptions import ValidationError

from . import ResourcePlugin, settings


class VlanRes(ResourcePlugin):
    name = 'vlan'
    verbose_name = 'Vlan'
    unit = 'tags'
    max_req = 1
    dflt_req = 0
    producers = [None]
    consumers = ['slices.Slice']
    
    def clean_req(self, resource):
        print 'hola'
        if resource.req > 1:
            raise ValidationError("Vlan resource request must be <= 1")


class DiskRes(ResourcePlugin):
    name = 'disk'
    verbose_name = 'Disk space'
    unit = 'MiB'
    max_req = settings.RESOURCES_DEFAULT_DISK_MAX_REQ
    dflt_req = settings.RESOURCES_DEFAULT_DISK_DFLT_REQ
    producers = ['nodes.Node']
    consumers = ['slices.Slice', 'slices.Sliver']


class Pub4Res(ResourcePlugin):
    name = 'pub_ipv6'
    verbose_name = 'Public IPv6 addresses'
    unit = 'addrs'
    max_req = settings.RESOURCES_DEFAULT_PUB4_MAX_REQ
    dflt_req = settings.RESOURCES_DEFAULT_PUB4_DFLT_REQ
    producers = ['nodes.Node']


class Pub6Res(ResourcePlugin):
    name = 'pub_ipv4'
    verbose_name = 'Public IPv4 addresses'
    unit = 'addrs'
    max_req = settings.RESOURCES_DEFAULT_PUB6_MAX_REQ
    dflt_req = settings.RESOURCES_DEFAULT_PUB6_DFLT_REQ
    producers = ['nodes.Node']
from django.core.exceptions import ValidationError

from . import ResourcePlugin


class VlanRes(ResourcePlugin):
    name = 'vlan'
    unit = 'tags'
    max_sliver = 1
    dflt_sliver = 0
    providers = [None]
    
    def validate_req(self, value):
        if value > 1:
            raise ValidationError("Vlan resource request must be <= 1")


class DiskRes(ResourcePlugin):
    name = 'disk'
    unit = 'MiB'
    providers = ['nodes.Node']
    consumers = ['slices.Slice', 'slices.Sliver']


class Pub4Res(ResourcePlugin):
    name = 'pub_ipv6'
    unit = 'addrs'
    providers = ['nodes.Node']


class Pub6Res(ResourcePlugin):
    name = 'pub_ipv4'
    unit = 'addrs'
    providers = ['nodes.Node']

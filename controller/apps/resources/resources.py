from django.core.exceptions import ValidationError

from . import ResourcePlugin, settings


class VlanRes(ResourcePlugin):
    name = 'vlan'
    verbose_name = 'Vlan'
    unit = 'tags'
    max_sliver = 1
    dflt_sliver = 0
    producers = [None] #TODO: implement testbed resources
    # Disabling VLAN consumers because this resource is managed directly
    # on Slice class. In future a generic management will be used but now
    # is fully implemented. See feature #46 note-56 for more information.
    #consumers = ['slices.Slice']
    
    def clean_req(self, resource):
        if resource.req > 1:
            raise ValidationError("Vlan resource request must be <= 1")
    
    def save(self, resource):
        obj = resource.content_object
        if resource.req == 0: # Never happens, is cleaned before saving
            obj.vlan_nr = None
        elif resource.req == 1:
            obj.vlan_nr = -1
        else:
            assert "Vlan resource request must be <= 1"
        obj.update_set_state()
    
    def delete(self, resource):
        obj = resource.content_object
        obj.vlan_nr = None
        obj.update_set_state()


class DiskRes(ResourcePlugin):
    name = 'disk'
    verbose_name = 'Disk space'
    unit = 'MiB'
    max_sliver = settings.RESOURCES_DEFAULT_DISK_MAX_SLIVER
    dflt_sliver = settings.RESOURCES_DEFAULT_DISK_DFLT_SLIVER
    producers = ['nodes.Node']
    consumers = ['slices.Slice', 'slices.Sliver']


class Pub4Res(ResourcePlugin):
    name = 'pub_ipv6'
    verbose_name = 'Public IPv6 addresses'
    unit = 'addrs'
    max_sliver = settings.RESOURCES_DEFAULT_PUB4_MAX_SLIVER
    dflt_sliver = settings.RESOURCES_DEFAULT_PUB4_DFLT_SLIVER
    producers = ['nodes.Node']


class Pub6Res(ResourcePlugin):
    name = 'pub_ipv4'
    verbose_name = 'Public IPv4 addresses'
    unit = 'addrs'
    max_sliver = settings.RESOURCES_DEFAULT_PUB6_MAX_SLIVER
    dflt_sliver = settings.RESOURCES_DEFAULT_PUB6_DFLT_SLIVER
    producers = ['nodes.Node']

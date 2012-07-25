from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from nodes.models import Node, Interface

import settings 

from slices import managers

from user_management import models as user_m_models

from django.template.defaultfilters import slugify


class Slice(models.Model):
    template = models.ForeignKey("SliverTemplate",
                                 verbose_name = "template",
                                 blank = True,
                                 null = True)
    confine_permissions = generic.GenericRelation(user_m_models.ConfinePermission,
                                                 verbose_name = "confine permission")
    
    
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique = True)
    user = models.ForeignKey(User)
    research_group = models.ForeignKey(user_m_models.ResearchGroup,
                                       blank = True,
                                       null = True)
    state = models.CharField(max_length=16,
                             choices=settings.STATE_CHOICES,
                             default=settings.DEFAULT_SLICE_STATE)

    write_size = models.IntegerField(default=0)
    code = models.FileField(upload_to=settings.CODE_DIR, blank=True)

    # Added for barebones
    vlan_nr = models.IntegerField(verbose_name = "vlan number")
    exp_data_uri = models.URLField(verbose_name = "exp data URI")
    exp_data_sha256 = models.CharField(max_length = 150,
                                   verbose_name = "exp data sha256")
    set_state = models.CharField(max_length=16,
                                 choices=settings.STATE_CHOICES,
                                 default=settings.DEFAULT_SLICE_STATE)
    uuid = models.CharField(max_length = 150,
                            verbose_name = "UUID",
                            unique = True)
    pubkey = models.TextField(verbose_name = "public key")
    expires = models.DateField(verbose_name = "expires at")
    serial = models.IntegerField(verbose_name = "serial")
    new_sliver_serial = models.IntegerField(verbose_name = "new sliver serial")

    objects = managers.SliceManager()
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Slice, self).save(*args, **kwargs)
    
class Sliver(models.Model):
    confine_permissions = generic.GenericRelation(user_m_models.ConfinePermission,
                                                  verbose_name = "confine permission")
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey(Node)

    ipv4_address = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
    ipv6_address = models.GenericIPAddressField(protocol='IPv6', blank=True, null=True)

    # Added for BareBones
    serial = models.IntegerField(verbose_name = "serial")


    # A-HACK params
    state = models.CharField(max_length=16,
                             choices=settings.STATE_CHOICES,
                             default=settings.DEFAULT_SLIVER_STATE,
                             blank=True)
    nr = models.IntegerField(blank=True)
    
    class Meta:
        unique_together = ('slice', 'node')
    
    def __unicode__(self):
        return "%s:%s" % (self.slice, self.node)
    
    def _provide_number(self):
        try: self.nr = self.__class__._default_manager.filter(node=self.node).order_by('-nr')[0].nr + 1
        except IndexError: self.nr = 1     

    def save(self, *args, **kwargs):
        if not self.pk: 
            self._provide_number()
            if not self.state: self.state=settings.DEFAULT_SLIVER_STATE
        super(Sliver, self).save(*args, **kwargs)

#    @property
#    def ipv4_address(self):
#        return "%s.%s" % (settings.IPV4_PREFIX, self.id)

#    @property
#    def ipv6_address(self):
#        id = hex(self.id)[2:]
#        return "%s:ffff::%s:0" % (settings.IPV6_PREFIX, id)

class SliverTemplate(models.Model):
    name = models.CharField(max_length = 200,
                            verbose_name = "name")
    template_type = models.CharField(max_length = 50,
                                     verbose_name = "type")
    arch = models.CharField(max_length = 50,
                            verbose_name = "architecture")
    enabled = models.BooleanField(verbose_name = "enabled")
    data_uri = models.URLField(verbose_name = "data URI")
    data_sha256 = models.CharField(max_length = 150,
                                   verbose_name = "sha256")

    def __unicode__(self):
        return self.name

class MemoryRequest(models.Model):
    sliver = models.OneToOneField(Sliver)
    min = models.BigIntegerField()
    max = models.BigIntegerField()

    def __unicode__(self):
        return "%s-%s" % (self.min, self.max)

class StorageRequest(models.Model):
    sliver = models.OneToOneField(Sliver)
    type = models.CharField(max_length=128, choices=settings.STORAGE_CHOICES, default=settings.DEFAULT_STORAGE)
    size = models.IntegerField()

    def __unicode__(self):
        return "%s:%s" % (self.type, self.size)

class CPURequest(models.Model):
    sliver = models.OneToOneField(Sliver)
    type = models.CharField(max_length=16, choices=settings.CPU_REQUEST_CHOICES, default=settings.DEFAULT_CPU_REQUEST)
    value = models.IntegerField()

    def __unicode__(self):
        return "%s:%s" % (self.type, self.value)

class NetworkRequest(models.Model):
    sliver = models.ForeignKey(Sliver)
    interface = models.ForeignKey(Interface,
                                  related_name = 'network_requests',
                                  blank = True,
                                  null = True)

    number = models.IntegerField(blank=True)
    type = models.CharField(max_length=16,
                            choices=settings.NETWORK_REQUESRT_CHOICES,
                            default=settings.DEFAULT_NETWORK_REQUEST)
    mac_address = models.CharField(max_length=18, blank=True)
    ipv4_address = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
    ipv6_address = models.GenericIPAddressField(protocol='IPv6', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def _provide_number(self):
        try: self.number = self.__class__._default_manager.filter(sliver__node=self.sliver.node).order_by('-number')[0].number + 1
        except IndexError: self.number = 0        

    def save(self, *args, **kwargs):
        if not self.pk: self._provide_number()
        super(NetworkRequest, self).save(*args, **kwargs)

    @property
    def name(self):
        return "eth%s" % self.number 

#    @property
#    def mac_address(self):
#        node = hex(self.sliver.node.id)[2:]
#        node = ('0' * (4-len(node))) + node
#        node = "%s:%s" % (node[0:2], node[2:4])
#        sliver = hex(self.sliver.number)[2:]
#        sliver = (('0' * (2-len(sliver))) + sliver)[0:2]
#        interface = hex(self.number)[2:]
#        interface = (('0' * (2-len(interface))) + interface)[0:2]
#        return "%s:%s:%s:%s" % (settings.MAC_PREFIX, node, sliver, interface)
#        
#    @property
#    def ip_address(self):
#        if self.type == settings.PUBLIC:
#            node = hex(self.sliver.node.id)[2:]
#            sliver = hex(self.sliver.id)[2:]
#            interface = hex(self.number)[2:]
#            return "%s:%s::%s:%s" % (settings.IPV6_PREFIX, node, sliver, interface)
#        return 'unassigned'
        

class SliverIface(models.Model):
    nr = models.IntegerField(verbose_name = "number")
    name = models.CharField(max_length = 200,
                            verbose_name = "name")

    # A-HACK params
    mac_addr = models.CharField(max_length = 200,
                                verbose_name = "mac address",
                                blank = True,
                                null = True)

class IsolatedIface(SliverIface):
    sliver = models.ForeignKey(Sliver)
    parent = models.ForeignKey(Interface,
                               verbose_name = "parent")

    def parent_name(self):
        self.parent.name

class IpSliverIface(SliverIface):
    use_default_gw = models.BooleanField(verbose_name = "use default gateway")

    # A-HACK params
    ipv6_addr = models.GenericIPAddressField(protocol='IPv6', blank=True, null=True)
    ipv4_addr = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)

class PublicIface(IpSliverIface):
    sliver = models.ForeignKey(Sliver)
    nr = models.IntegerField(verbose_name = "number")

class PrivateIface(IpSliverIface):
    sliver = models.ForeignKey(Sliver)
    nr = models.IntegerField(verbose_name = "number")

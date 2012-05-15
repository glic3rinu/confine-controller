from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from nodes.models import Node, Interface

import settings 

from slices import managers

from user_management import models as user_m_models


class Slice(models.Model):
    global_permissions = generic.GenericRelation(user_m_models.GlobalPermission,
                                                 verbose_name = "global permission")
    discrete_permissions = generic.GenericRelation(user_m_models.DiscretePermission,
                                                 verbose_name = "discrete permission")
    
    name = models.CharField(max_length=255, unique=True)
    research_group = models.ForeignKey(user_m_models.ResearchGroup)
    state = models.CharField(max_length=16, choices=settings.STATE_CHOICES, default=settings.DEFAULT_SLICE_STATE)
    template = models.FilePathField(path=settings.TEMPLATE_DIR, recursive=True)
    write_size = models.IntegerField(default=0)
    code = models.FileField(upload_to=settings.CODE_DIR, blank=True)

    objects = managers.SliceManager()
    
    def __unicode__(self):
        return self.name
    
class Sliver(models.Model):
    global_permissions = generic.GenericRelation(user_m_models.GlobalPermission,
                                                 verbose_name = "global permission")
    discrete_permissions = generic.GenericRelation(user_m_models.DiscretePermission,
                                                 verbose_name = "discrete permission")
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey(Node)
    state = models.CharField(max_length=16, choices=settings.STATE_CHOICES, default=settings.DEFAULT_SLIVER_STATE, blank=True)
    number = models.IntegerField(blank=True)
    ipv4_address = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
    ipv6_address = models.GenericIPAddressField(protocol='IPv6', blank=True, null=True)
    
    class Meta:
        unique_together = ('slice', 'node')
    
    def __unicode__(self):
        return "%s:%s" % (self.slice, self.node)
    
    def _provide_number(self):
        try: self.number = self.__class__._default_manager.filter(node=self.node).order_by('-number')[0].number + 1
        except IndexError: self.number = 1     

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
    number = models.IntegerField(blank=True)
    type = models.CharField(max_length=16, choices=settings.NETWORK_REQUESRT_CHOICES, default=settings.DEFAULT_NETWORK_REQUEST)
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
        


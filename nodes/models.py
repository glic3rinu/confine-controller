from django.db import models
from django.contrib.auth import models as auth_models

import settings

class Node(models.Model):
    hostname = models.CharField(max_length=255, unique=True)
    url = models.URLField("URL", blank=True)
    architecture = models.CharField(max_length=128, choices=settings.ARCHITECTURE_CHOICES, default=settings.DEFAULT_ARCHITECTURE)
    #TODO: use GeoDjango ? 
    latitude = models.CharField(max_length=255, blank=True)
    longitude = models.CharField(max_length=255, blank=True)
    uci = models.TextField(blank=True)
    public_key = models.TextField(blank=True)
    state = models.CharField(max_length=32, choices=settings.NODE_STATE_CHOICES, default=settings.DEFAULT_NODE_STATE)
    ip = models.IPAddressField(verbose_name = "ip")
    owner = models.ForeignKey(auth_models.User,
                              verbose_name = "owner",
                              blank = True,
                              null = True)
        
    def __unicode__(self):
        return self.hostname
    
    def port(self):
        return "2222"

    @property
    def tinc_name(self):
        return "node_%s" % self.id
    
    @property
    def tinc_public_key(self):
        return self.public_key
    
    @property
    def local_ip(self):
        return '"TODO: local ipv6 iface"'

    

class DeleteRequest(models.Model):
    node = models.ForeignKey("Node",
                             verbose_name = "node")

    def __unicode__(self):
        return self.node.hostname
    
class Storage(models.Model):
    node = models.OneToOneField(Node)
    types = models.CharField(max_length=128)
    size = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Storage'

class Memory(models.Model):
    node = models.OneToOneField(Node)
    size = models.BigIntegerField(null=True)

    class Meta:
        verbose_name_plural = 'Memory'

class CPU(models.Model):
    node = models.OneToOneField(Node)
    model = models.CharField(max_length=64, blank=True)
    number = models.IntegerField(default='1')
    frequency = models.CharField(max_length=64, blank=True)

    class Meta:
        verbose_name_plural = 'CPU'

class Interface(models.Model):
    node = models.ForeignKey(Node)
    name = models.CharField(max_length=8, help_text='e.g. eth1')
    type = models.CharField(max_length=255, choices=settings.IFACE_TYPE_CHOICES, default=settings.DEFAULT_IFACE_TYPE)
    
    def __unicode__(self):
        return self.name




from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from nodes.models import CnHost
import settings


class Host(models.Model):
    description = models.CharField(max_length=256)
    admin = models.ForeignKey(User)


class TincHost(models.Model):
    tinc_name = models.CharField(max_length=64, unique=True)
    tinc_pubkey = models.TextField(unique=True, 
        help_text="PEM-encoded RSA public key used on tinc management network.")
    connect_to = models.ManyToManyField('tinc.TincAddress', blank=True)
    
    class Meta:
        abstract = True

    def __unicode__(self):
        return self.tinc_name


class Gateway(CnHost):
    #TODO: ID >= 2
    pass


class TincServer(TincHost):
    gateway = models.OneToOneField(Gateway)


class Island(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name


class TincAddress(models.Model):
    ip_addr = models.GenericIPAddressField(protocol='IPv6', 
        help_text="The IPv6 address of this tinc address.")
    port = models.SmallIntegerField(default=settings.TINC_DEFAULT_PORT, 
        help_text="The TCP/UDP port of this tinc address.")
    island = models.ForeignKey(Island, help_text="""The <a 
        href="http://wiki.confine-project.eu/arch:rest-api#island_at_server">island</a> 
        this tinc address is reachable from.""")
    server = models.ForeignKey(TincServer)
    
    class Meta:
        verbose_name_plural = 'Tinc Addresses'
    
    def __unicode__(self):
        return str(self.ip_addr)


class TincClient(TincHost):
    islands = models.ManyToManyField(Island, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    class Meta:
        unique_together = ('content_type', 'object_id')

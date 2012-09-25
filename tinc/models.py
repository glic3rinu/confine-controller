from django.db import models
import settings


class Island(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name


class TincAddress(models.Model):
    ip_addr = models.GenericIPAddressField(verbose_name="IP Address", protocol='IPv6')
    port = models.SmallIntegerField(default=settings.TINC_DEFAULT_PORT)
    island = models.ForeignKey(Island)
    server = models.ForeignKey('tinc.TincServer')
    
    class Meta:
        verbose_name_plural = 'Tinc Addresses'
    
    def __unicode__(self):
        return str(self.ip_addr)


class TincHost(models.Model):
    tinc_name = models.CharField(max_length=64)
    tinc_pubkey = models.TextField(verbose_name="Public Key")
    connect_to = models.ManyToManyField(TincAddress, blank=True)
    
    class Meta:
        abstract = True

    def __unicode__(self):
        return self.tinc_name


class TincClient(TincHost):
    islands = models.ManyToManyField(Island, blank=True)
    
    class Meta:
        abstract = True

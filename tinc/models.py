from django.db import models
import settings


class TincHost(models.Model):
    tinc_name = models.CharField(max_length=64, unique=True)
    tinc_pubkey = models.TextField(unique=True, verbose_name="Tinc Public Key")
    connect_to = models.ManyToManyField('tinc.TincAddress', blank=True)
    
    class Meta:
        abstract = True

    def __unicode__(self):
        return self.tinc_name


class Gateway(TincHost):
    #TODO: ID >= 2
    pass


class Island(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name


class TincAddress(models.Model):
    ip_addr = models.GenericIPAddressField(verbose_name="IPv6 Address", protocol='IPv6')
    port = models.SmallIntegerField(default=settings.TINC_DEFAULT_PORT)
    island = models.ForeignKey(Island)
    server = models.ForeignKey(Gateway)
    
    class Meta:
        verbose_name_plural = 'Tinc Addresses'
    
    def __unicode__(self):
        return str(self.ip_addr)


class TincClient(TincHost):
    islands = models.ManyToManyField(Island, blank=True)
    
    class Meta:
        abstract = True

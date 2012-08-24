from django.db import models
from django.contrib.auth import models as auth_models

import settings

class Island(models.Model):
    name = models.CharField(max_length = 200,
                            verbose_name = "name")

    def __unicode__(self):
        return self.name

class TincAddress(models.Model):
    island = models.ForeignKey("Island",
                               verbose_name = "island")
    ip_addr = models.IPAddressField(verbose_name="ip address")
    port = models.CharField(max_length = 10,
                                 verbose_name = "port")
    

class TincHost(models.Model):
    name = models.CharField(max_length = 200,
                                 verbose_name = "name")
    pubkey = models.TextField(verbose_name = "pubkey")
    connect_to = models.ManyToManyField("TincAddress",
                                        related_name = "host_connect_to",
                                        blank = True,
                                        null = True
                                        )

class TincClient(TincHost):
    island = models.ManyToManyField("Island",
                                    verbose_name = "island")

class TincServer(TincHost):
    tinc_address = models.ForeignKey("TincAddress",
                                     verbose_name = "tinc address")


class Gateway(TincServer):
    cn_url = models.URLField("URL", blank=True)

class Host(TincClient):
    admin = models.ForeignKey(auth_models.User,
                              verbose_name = "admin")

class NodeProps(models.Model):
    node = models.ForeignKey("Node",
                             verbose_name = "node")
    
    name = models.CharField(max_length = 150,
                            verbose_name = "name")
    value = models.CharField(max_length = 200,
                             verbose_name = "value")

class Node(TincClient):
    hostname = models.CharField(max_length=255)
    cn_url = models.URLField("URL", blank=True)

    #TODO: use GeoDjango ? 
    latitude = models.CharField(max_length=255, blank=True)
    longitude = models.CharField(max_length=255, blank=True)
    ip = models.IPAddressField(verbose_name = "ip")
    admin = models.ForeignKey(auth_models.User,
                              verbose_name = "admin")

    # Added for barebones
    set_state = models.CharField(max_length=32,
                              choices=settings.NODE_STATE_CHOICES,
                              default=settings.DEFAULT_NODE_STATE)
    sliver_public_ipv4_total = models.IntegerField(verbose_name = "rd public IPv4 total",
                                                   default = 1)
    priv_ipv4_prefix = models.CharField(max_length = 50,
                                        verbose_name = "private ipv4 prefix",
                                        blank = True,
                                        null = True)
    sliver_mac_prefix = models.CharField(max_length = 50,
                                         default = "0x200",
                                         verbose_name = "sliver MAC prefix")
    cn_url = models.URLField(blank=True,
                             null = True,
                             verbose_name = "cn url")
    cndb_uri = models.URLField(blank=True,
                               null = True,
                               verbose_name = "cndb uri")
    cndb_cached = models.DateTimeField(blank=True,
                                       null = True,
                                       verbose_name = "cndb cached")

    rd_uuid = models.CharField(max_length = 150,
                            verbose_name = "research device UUID",
                            unique = True)
    rd_pubkey = models.TextField(verbose_name = "research device public key")
    rd_cert = models.TextField(verbose_name = "research device certificate")
    rd_boot_sn = models.IntegerField(verbose_name = "research device boot serial number")
    rd_arch = models.CharField(max_length=128,
                               choices=settings.ARCHITECTURE_CHOICES,
                               default=settings.DEFAULT_ARCHITECTURE)
    rd_local_iface = models.CharField(max_length = 200,
                                      default = "eth0",
                                      verbose_name = "research device local interface")
    rd_cn_url = models.URLField(blank=True,
                                null = True,
                                verbose_name = "research device cn url")
    rd_cndb_uri = models.URLField(blank=True,
                                  null = True,
                                  verbose_name = "research device cndb uri")
    rd_cndb_cached = models.DateTimeField(blank=True,
                                          null = True,
                                          verbose_name = "research device cndb cached")

    

    # A-HACK params
    uci = models.TextField(blank=True)
    state = models.CharField(max_length=32,
                             choices=settings.NODE_STATE_CHOICES,
                             default=settings.DEFAULT_NODE_STATE)
    sliver_public_ipv4_avail = models.IntegerField(verbose_name = "rd public IPv4 available",
                                                   blank = True,
                                                   null = True)
        
    def __unicode__(self):
        return self.hostname
    
    def port(self):
        return "2222"

    @property
    def interface_ids(self):
        return map(lambda a: unicode(a.id), self.interface_set.all())

    @property
    def public_key(self):
        return self.rd_pubkey
    
    @property
    def local_ip(self):
        return '"TODO: local ipv6 iface"'

    @property
    def ipv6(self):
        #return "%s:%s:0000::2" % (settings.TESTBED_BASE_IP,
        #                          self.hex_id)
        return self.ip

    @property
    def hex_id(self):
        return "%X" % self.id
    

class DeleteRequest(models.Model):
    node = models.ForeignKey("Node",
                             verbose_name = "node")

    def __unicode__(self):
        return self.node.hostname

class Storage(models.Model):
    node = models.OneToOneField(Node)
    types = models.CharField(max_length=128,
                             null = True,
                             blank = True,
                             choices = settings.STORAGE_CHOICES)
    size = models.IntegerField(null = True,
                               blank = True)

    class Meta:
        verbose_name_plural = 'Storage'

class Memory(models.Model):
    node = models.OneToOneField(Node)
    size = models.BigIntegerField(null=True,
                                  blank = True)

    class Meta:
        verbose_name_plural = 'Memory'

class CPU(models.Model):
    node = models.OneToOneField(Node)
    model = models.CharField(max_length=64,
                             blank=True,
                             null = True)
    number = models.IntegerField(default='1',
                                 null = True,
                                 blank = True)
    frequency = models.CharField(max_length=64, blank=True,
                                 null = True)

    class Meta:
        verbose_name_plural = 'CPU'

class Interface(models.Model):
    node = models.ForeignKey(Node)
    name = models.CharField(max_length=8, help_text='e.g. eth1')
    type = models.CharField(max_length=255, choices=settings.IFACE_TYPE_CHOICES, default=settings.DEFAULT_IFACE_TYPE)
    channel = models.IntegerField(blank = True,
                                  null = True,
                                  verbose_name = "channel")
    essid = models.CharField(max_length = "150",
                             blank = True,
                             null = True,
                             verbose_name = "essid")
    
    def __unicode__(self):
        return "%s - %s" % (self.node.hostname, self.name)




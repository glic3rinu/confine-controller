from django.db import models
import settings

class Node(models.Model):
    hostname = models.CharField(max_length=255)
    url = models.URLField("URL", blank=True)
    architecture = models.CharField(max_length=128, choices=settings.ARCHITECTURE_CHOICES, default=settings.DEFAULT_ARCHITECTURE)
    #TODO: use GeoDjango ? 
    latitude = models.CharField(max_length=255, blank=True)
    longitude = models.CharField(max_length=255, blank=True)
    uci = models.FileField("UCI", upload_to=settings.UCI_DIR, blank=True)
    public_key = models.TextField()
    status = models.CharField(max_length=32, choices=settings.NODE_STATUS_CHOICES, default=settings.DEFAULT_NODE_STATUS)
    
    def __unicode__(self):
        return self.hostname

    @property
    def tinc_name(self):
        return "node_%s" % self.id
    
    @property
    def tinc_public_key(self):
        return self.public_key

class DeleteRequest(models.Model):
    node = models.ForeignKey("Node",
                             verbose_name = "node")
    
    
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

class Link(models.Model):
    node = models.ForeignKey(Node)
    status = models.CharField(max_length=32, choices=settings.LINK_STATUS_CHOICES, default=settings.DEFAULT_LINK_STATUS)
    connected_to = models.ManyToManyField(Node, related_name='connected_to', blank=True)
    

class CommunityLink(Link): pass

class GatewayLink(Link): pass

class LocalLink(Link): pass

class DirectLink(Link): pass


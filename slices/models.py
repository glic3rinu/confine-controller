from django.db import models
from django.contrib.auth.models import User
from nodes.models import Node, Interface
import settings 

class Slice(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User)
    state = models.CharField(max_length=16, choices=settings.STATE_CHOICES, default=settings.DEFAULT_SLICE_STATE)
    template = models.FilePathField(path=settings.TEMPLATE_DIR, recursive=True)
    write_size = models.IntegerField(default=0)
    code = models.FileField(upload_to=settings.CODE_DIR, blank=True)
    
    def __unicode__(self):
        return self.name
    
class Sliver(models.Model):
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey(Node)
    state = models.CharField(max_length=16, choices=settings.STATE_CHOICES, default=settings.DEFAULT_SLIVER_STATE)
    
    class Meta:
        unique_together = ('slice', 'node')
    
    def __unicode__(self):
        return "%s:%s" % (self.slice, self.node)
    
    
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
    type = models.CharField(max_length=16, choices=settings.NETWORK_REQUESRT_CHOICES, default=settings.DEFAULT_NETWORK_REQUEST)
    min_rate = models.IntegerField(null=True)
    max_rate = models.IntegerField(null=True)
    max_throughput = models.IntegerField(null=True)
    
    def __unicode__(self):
        return "%s:(%s-%s):%s" % (self.type, self.min_rate, self.max_rate, self.max_throughput)    


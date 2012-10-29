from common.fields import MultiSelectField
from django.db import models
from firmware import settings
from nodes.settings import NODE_ARCHS
from singleton_models.models import SingletonModel


class FirmwareBuild(models.Model)
    node = models.ForeignKey('nodes.Node')
    file = models.FileField(upload_to=settings.FIRMWARE_DIR)
    date = models.DateTimeField(auto_now_add=True)
    version = CharField(max_length=64)


class FirmwareConfig(SingletonModel):
    description = CharField(max_length=255)
    version = CharField(max_length=64)
    date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "firmware config"
        verbose_name_plural = "firmware config"
    
    def __unicode__(self):
        return 'Current Firmware Config'
    
    @classmethod
    def build(cls, node):


class BaseImage(models.Model):
    config = models.ForeignKey(FirmwareConfig)
    architectures = MultiSelectField(max_length=250, choices=NODE_ARCHS)
    image = models.FileField(upload_to=settings.FIRMWARE_DIR)


class FirmwareConfigUCI(models.Model):
    config = models.ForeignKey(FirmwareConfig)
    section = models.CharField(max_length=32, help_text="UCI config statement")
    option = models.CharField(max_lenght=32, help_text="UCI option statement")
    value = models.CharField(max_lenght=255, help_text="""Python code for obtining 
        the value. i.e. node.properties['ip']""")



class FirmwareBuildUCI(BaseUCI):
    build = models.ForeignKey(FirmwareBuild)
    section = models.CharField(max_length=32, help_text="UCI config statement")
    option = models.CharField(max_lenght=32, help_text="UCI option statement")
    value = models.CharField(max_lenght=255)


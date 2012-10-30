from common.fields import MultiSelectField
from django.core.exceptions import ValidationError
from django.db import models
from firmware import settings
from nodes.settings import NODE_ARCHS
from singleton_models.models import SingletonModel


class FirmwareBuild(models.Model):
    node = models.ForeignKey('nodes.Node')
    date = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=64)
    image = models.FileField(upload_to=settings.FIRMWARE_DIR)
    
    def __unicode__(self):
        return self.node.description

class FirmwareConfig(SingletonModel):
    description = models.CharField(max_length=255)
    version = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "firmware config"
        verbose_name_plural = "firmware config"
    
    def __unicode__(self):
        return 'Current Firmware Config'
    
    def build(self, node):
        # TODO how to get public_ipv4_avail ?
        from confw import confw
        arch_regex = "(^|\s)%s(,|$)" % node.arch
        base_image = BaseImage.objects.get(architectures__regex=arch_regex).image
        template = confw.template('generic', 'confine', basedir='/tmp/templates/')
        files = confw.files('generic', basedir='/tmp/files/')
        build_uci = []
        for uci in self.firmwareconfiguci_set.all():
            value = eval(uci.value)
            template.set(uci.section, uci.option, value)
            build_uci.append({'section': uci.section, 
                'option': uci.option, 
                'value': value})
        image = confw.image(template, files)
        image.build(base_image.path, gzip=True)
        image.clean()
        # TODO iamge.path
        # Create FirmwareBuild object
        build = FirmwareBuild.objects.create(node=node, version=self.version,
            image=image.path)
        for uci in build_uci:
            FirmwareBuildUCI.objects.create(build=build, **uci)


class BaseImage(models.Model):
    config = models.ForeignKey(FirmwareConfig)
    architectures = MultiSelectField(max_length=250, choices=NODE_ARCHS)
    image = models.FileField(upload_to=settings.FIRMWARE_DIR)
    
    def __unicode__(self):
        return ", ".join(self.architectures)
    
    def clean(self):
        """ prevent repeated architectures """
        for arch in self.architectures:
            arch_regex = "(^|\s)%s(,|$)" % arch
            try: existing = BaseImage.objects.get(architectures__regex=arch_regex)
            except BaseImage.DoesNotExist: pass
            else:
                if existing and (not self.pk or existing.pk != self.pk):
                    raise ValidationError("%s already present" % arch)
        super(BaseImage, self).clean()


class FirmwareConfigUCI(models.Model):
    config = models.ForeignKey(FirmwareConfig)
    section = models.CharField(max_length=32, help_text="UCI config statement",
        default='node')
    option = models.CharField(max_length=32, help_text="UCI option statement")
    value = models.CharField(max_length=255, help_text="""Python code for obtining 
        the value. i.e. node.properties['ip']""")
    # TODO Add validation field
    
    class Meta:
        unique_together = ['config', 'section', 'option']
    
    def __unicode__(self):
        return "%s.%s" % (self.section, self.option)


class FirmwareBuildUCI(models.Model):
    build = models.ForeignKey(FirmwareBuild)
    section = models.CharField(max_length=32, help_text="UCI config statement")
    option = models.CharField(max_length=32, help_text="UCI option statement")
    value = models.CharField(max_length=255)


from common.fields import MultiSelectField
from common.models import generate_chainer_manager
from django.core.exceptions import ValidationError
from django.db import models
from firmware import settings
from nodes.settings import NODE_ARCHS
from singleton_models.models import SingletonModel


class QueueQuerySet(models.query.QuerySet):
    def get_current(self, node):
        build = Build.objects.get(node=node)
        config = Config.objects.get()
        if build.match(config): return build
        else: raise Build.DoesNotExist()


class Build(models.Model):
    node = models.OneToOneField('nodes.Node')
    date = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=64)
    image = models.FileField(upload_to=settings.FIRMWARE_DIR)
    
    objects = generate_chainer_manager(QueueQuerySet)
    
    def __unicode__(self):
        return self.node.description
    
    @classmethod
    def build(cls, node):
        try: old_build = cls.objects.get(node=node)
        except cls.DoesNotExist: pass
        else: old_build.delete()
        # TODO delete image file
        Config.objects.get().build(node)
    
    def get_uci(self):
        return self.builduci_set.all()
    
    def match(self, config):
        if self.version != config.version: 
            return False
        ucis = set(self.get_uci().values_list('section', 'option', 'value'))
        get = lambda u: (u.section, u.option, u.get_value(self.node))
        config_ucis = set(map(get, config.get_uci()))
        return ucis == config_ucis


class Config(SingletonModel):
    description = models.CharField(max_length=255)
    version = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Firmware Config"
        verbose_name_plural = "Firmware Config"
    
    def __unicode__(self):
        return 'Current Firmware Config'
    
    def get_uci(self):
        return self.configuci_set.all()
    
    def build(self, node):
        # TODO how to get public_ipv4_avail ?
        from confw import confw
        arch_regex = "(^|,)%s(,|$)" % node.arch
        base_image = BaseImage.objects.get(architectures__regex=arch_regex).image
#        template = confw.template('generic', 'confine', basedir='/tmp/templates/')
#        files = confw.files('generic', basedir='/tmp/files/')
        build_uci = []
        for uci in self.get_uci():
            value = uci.get_value(node)
#            template.set(uci.section, uci.option, value)
            build_uci.append({'section': uci.section, 
                'option': uci.option, 
                'value': value})
#        image = confw.image(template, files)
#        image.build(base_image.path, gzip=True)
#        image.clean()
        # TODO iamge.path
        # Create Build object
        build = Build.objects.create(node=node, version=self.version,
            image='firmwares/openwrt-x86-generic-combined-ext4-40.img.gz')
        for uci in build_uci:
            BuildUCI.objects.create(build=build, **uci)


class BaseImage(models.Model):
    config = models.ForeignKey(Config)
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


class ConfigUCI(models.Model):
    config = models.ForeignKey(Config)
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
    
    def get_value(self, node):
        return unicode(eval(self.value))


class BuildUCI(models.Model):
    build = models.ForeignKey(Build)
    section = models.CharField(max_length=32, help_text="UCI config statement")
    option = models.CharField(max_length=32, help_text="UCI option statement")
    value = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ['build', 'section', 'option']
    
    def __unicode__(self):
        return "%s.%s" % (self.section, self.option)


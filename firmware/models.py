from common.fields import MultiSelectField
from common.models import generate_chainer_manager
from django.core.exceptions import ValidationError
from django.db import models
from django_transaction_signals import defer
from firmware import settings
from firmware.tasks import build
from nodes.settings import NODE_ARCHS
from singleton_models.models import SingletonModel
import os


class QueueQuerySet(models.query.QuerySet):
    def get_current(self, node):
        build = Build.objects.get(node=node)
        config = Config.objects.get()
        if build.state != Build.AVAILABLE: return build
        if build.match(config): return build
        else: raise Build.DoesNotExist()


class Build(models.Model):
    REQUESTED = 'REQUESTED'
    QUEUED = 'QUEUED'
    BUILDING = 'BUILDING'
    AVAILABLE = 'AVAILABLE'
    OUTDATED = 'OUTDATED'
    DELETED = 'DELETED'
    FAILED = 'FAILED'
    
    node = models.OneToOneField('nodes.Node')
    date = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=64)
    image = models.FileField(upload_to=settings.FIRMWARE_DIR)
    task_id = models.CharField(max_length=36, unique=True)
    
    objects = generate_chainer_manager(QueueQuerySet)
    
    class Meta:
        ordering = ['-date']
    
    def __unicode__(self):
        return self.node.description
    
    def delete(self, *args, **kwargs):
        super(Build, self).delete(*args, **kwargs)
        try: os.remove(self.image.path)
        except: pass
    
    @property
    def task(self):
        from djcelery.models import TaskState
        if not self.task_id: return None
        try: return TaskState.objects.get(task_id=self.task_id)
        except TaskState.DoesNotExist: return None
    
    @property
    def state(self):
        if self.image: 
            try: self.image.file
            except IOError: return self.DELETED
            else: 
                config = Config.objects.get()
                if self.match(config): return self.AVAILABLE
                else: return self.OUTDATED
        if not self.task_id: return self.REQUESTED
        if self.task and self.task.state == 'RECEIVED': return self.QUEUED
        if self.task and self.task.state == 'STARTED': return self.BUILDING
        return self.FAILED
    
    @classmethod
    def build(cls, node, async=False):
        try: old_build = cls.objects.get(node=node)
        except cls.DoesNotExist: pass
        else: old_build.delete()
        config = Config.objects.get()
        build_obj = Build.objects.create(node=node, version=config.version)
        if async:
            defer(build.delay, build_obj.pk)
        else:
            build_obj = build(build_obj.pk)
        return build_obj
    
    def get_uci(self):
        return self.builduci_set.all()
    
    def match(self, config):
        if self.version != config.version: return False
        ucis = set(self.get_uci().values_list('section', 'option', 'value'))
        get = lambda uci: (uci.section, uci.option, uci.get_value(self.node))
        config_ucis = set(map(get, config.get_uci()))
        return ucis == config_ucis
    
    def add_uci(self, **kwargs):
        BuildUCI.objects.create(build=self, **kwargs)


class BuildUCI(models.Model):
    build = models.ForeignKey(Build)
    section = models.CharField(max_length=32, help_text="UCI config statement")
    option = models.CharField(max_length=32, help_text="UCI option statement")
    value = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ['build', 'section', 'option']
    
    def __unicode__(self):
        return "%s.%s" % (self.section, self.option)


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
    
    def get_image(self, node):
        arch_regex = "(^|,)%s(,|$)" % node.arch
        return self.baseimage_set.get(architectures__regex=arch_regex).image


class BaseImage(models.Model):
    config = models.ForeignKey(Config)
    architectures = MultiSelectField(max_length=250, choices=NODE_ARCHS)
    image = models.FileField(upload_to=settings.FIRMWARE_DIR)
    
    def __unicode__(self):
        return ", ".join(self.architectures)
    
    def clean(self):
        """ Prevent repeated architectures """
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
    # TODO Add validation field ?
    
    class Meta:
        unique_together = ['config', 'section', 'option']
    
    def __unicode__(self):
        return "%s.%s" % (self.section, self.option)
    
    def get_value(self, node):
        return unicode(eval(self.value))


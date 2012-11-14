from hashlib import sha256
import os

from celery import states as celery_states
from django.conf import settings as project_settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models
from django_transaction_signals import defer
from private_files import PrivateFileField
from singleton_models.models import SingletonModel

from common.fields import MultiSelectField
from common.models import generate_chainer_manager
from firmware import settings
from firmware.tasks import build
from nodes.settings import NODE_ARCHS


# TODO make this accessible in a common place: settings? controller? common? ..?
private_storage = FileSystemStorage(location=project_settings.PRIVATE_MEDIA_ROOT)


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
    # TODO: write condition method for preventing unauthorized downloads
    # http://django-private-files.readthedocs.org/en/latest/usage.html
    image = PrivateFileField(upload_to=settings.FIRMWARE_DIR, storage=private_storage)
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
        if self.task and self.task.state == celery_states.RECEIVED: return self.QUEUED
        if self.task and self.task.state == celery_states.STARTED: return self.BUILDING
        return self.FAILED
    
    @property
    def is_processing(self):
        return self.state in [self.REQUESTED, self.QUEUED, self.BUILDING]
    
    @property
    def is_available(self):
        return self.state == self.AVAILABLE
    
    @property
    def is_unavailable(self):
        return self.state in [self.OUTDATED, self.DELETED, self.FAILED]
    
    @property
    def image_sha256(self):
        try: return sha256(self.image.file.read()).hexdigest()
        except: return None
    
    @classmethod
    def build(cls, node, async=False):
        try: old_build = cls.objects.get(node=node)
        except cls.DoesNotExist: pass
        else: 
            #TODO: kill or prevent existing task if its running
            old_build.delete()
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
    section = models.CharField(max_length=32, help_text='UCI config statement')
    option = models.CharField(max_length=32, help_text='UCI option statement')
    value = models.CharField(max_length=255)
    
    class Meta:
        unique_together = ['build', 'section', 'option']
    
    def __unicode__(self):
        return "%s.%s" % (self.section, self.option)


class Config(SingletonModel):
    description = models.CharField(max_length=255)
    version = models.CharField(max_length=64)
    
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
    """
    Describes the image used for generating per node customized images.
    """
    config = models.ForeignKey(Config)
    architectures = MultiSelectField(max_length=250, choices=NODE_ARCHS)
    image = models.FileField(upload_to=settings.FIRMWARE_DIR)
    
    def __unicode__(self):
        return ", ".join(self.architectures)
    
    def clean(self):
        """ Prevent repeated architectures """
        #TODO: move this logic to formset validation
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
    section = models.CharField(max_length=32, help_text='UCI config statement',
        default='node')
    option = models.CharField(max_length=32, help_text='UCI option statement')
    value = models.CharField(max_length=255, 
        help_text='Python code that will be evaluated for obtining the value '
                  'from the node. For example: node.properties[\'ip\']')
    # TODO Add validation field ?
    
    class Meta:
        unique_together = ['config', 'section', 'option']
    
    def __unicode__(self):
        return "%s.%s" % (self.section, self.option)
    
    def get_value(self, node):
        return unicode(eval(self.value))


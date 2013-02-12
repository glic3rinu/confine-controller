import os
from hashlib import sha256

from celery import states as celery_states
from django import template
from django.conf import settings as project_settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.template import Template, Context
from django_transaction_signals import defer
from djcelery.models import TaskState
from private_files import PrivateFileField
from singleton_models.models import SingletonModel

from controller.models.fields import MultiSelectField
from controller.models.utils import generate_chainer_manager
from nodes.models import Server
from nodes.settings import NODES_NODE_ARCHS

from . import settings
from .tasks import build


private_storage = FileSystemStorage(location=project_settings.PRIVATE_MEDIA_ROOT)


class BuildQuerySet(models.query.QuerySet):
    def get_current(self, node):
        """
        Given an node returns an up-to-date builded image, if exists.
        """ 
        build = Build.objects.get(node=node)
        config = Config.objects.get()
        if build.state != Build.AVAILABLE: 
            return build
        if build.match(config):
            return build
        else: 
            raise Build.DoesNotExist()


class Build(models.Model):
    """
    Represents a builded image for a research device.
    """
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
    image = PrivateFileField(upload_to=settings.FIRMWARE_DIR, storage=private_storage,
        condition=lambda request, self:
                  request.user.has_perm('nodes.getfirmware_node', obj=self.node))
    task_id = models.CharField(max_length=36, unique=True, null=True, help_text="Celery Task ID")
    
    objects = generate_chainer_manager(BuildQuerySet)
    
    class Meta:
        ordering = ['-date']
    
    def __unicode__(self):
        return self.node.description
    
    def delete(self, *args, **kwargs):
        """
        Deletes the build and also the image file stored on the file system
        """
        super(Build, self).delete(*args, **kwargs)
        try:
            os.remove(self.image.path)
        except:
            pass
    
    @property
    def image_name(self):
        return self.image.name.split('/')[-1]
    
    @property
    def task(self):
        """
        Returns the celery task responsible for 'self' image build.
        """
        if not self.task_id:
            return None
        try:
            return TaskState.objects.get(task_id=self.task_id)
        except TaskState.DoesNotExist:
            return None
    
    @property
    def state(self):
        """ Gives the current state of the build """
        if self.image:
            try:
                self.image.file
            except IOError:
                return self.DELETED
            else: 
                config = Config.objects.get()
                if self.match(config):
                    return self.AVAILABLE
                else:
                    return self.OUTDATED
        if not self.task_id:
            return self.REQUESTED
        if self.task and self.task.state == celery_states.RECEIVED:
            return self.QUEUED
        if self.task and self.task.state == celery_states.STARTED:
            return self.BUILDING
        return self.FAILED
    
    @property
    def is_processing(self):
        """
        Abstract state, useful for rendering the appropiate message on the build page
        """
        return self.state in [self.REQUESTED, self.QUEUED, self.BUILDING]
    
    @property
    def is_available(self):
        """
        Abstract state, useful for rendering the appropiate message on the build page
        """
        return self.state == self.AVAILABLE
    
    @property
    def is_unavailable(self):
        """
        Abstract state, useful for rendering the appropiate message on the build page
        """
        return self.state in [self.OUTDATED, self.DELETED, self.FAILED]
    
    @property
    def image_sha256(self):
        try:
            return sha256(self.image.file.read()).hexdigest()
        except:
            return None
    
    @classmethod
    def build(cls, node, async=False, exclude=[]):
        """
        This method handles the building image,
        if async is True the building task will be executed with Celery
        """
        try:
            old_build = cls.objects.get(node=node)
        except cls.DoesNotExist:
            pass
        else: 
            if old_build.state == cls.BUILDING:
                raise cls.ConcurrencyError("One build at a time.")
            old_build.delete()
        config = Config.objects.get()
        build_obj = Build.objects.create(node=node, version=config.version)
        if async:
            defer(build.delay, build_obj.pk, exclude=exclude)
        else:
            build_obj = build(build_obj.pk, exclude=exclude)
        return build_obj
    
    def add_file(self, path, content, config):
        """ Add a new generated file to the build """
        BuildFile.objects.create(build=self, path=path, content=content, config=config)
    
    def match(self, config):
        """ Checks if a a given build is up-to-date or not """
        if self.version != config.version:
            return False
        config = Config.objects.get()
        exclude = config.files.optional().values_list('pk', flat=True)
        old_files = set( (f.path,f.content) for f in self.files.exclude(config__pk__in=exclude) )
        new_files = set( (f.path,f.content) for f in config.eval_files(self.node, exclude=exclude) )
        return new_files == old_files
    
    class ConcurrencyError(Exception):
        """ Exception related to building images concurrently (not supported) """
        pass


class BuildFile(models.Model):
    """ 
    Describes a file of a builded image
    """
    build = models.ForeignKey(Build, related_name='files')
    config = models.ForeignKey('firmware.ConfigFile', related_name='files')
    path = models.CharField(max_length=256)
    content = models.TextField()
    
    class Meta:
        unique_together = ('build', 'path')
    
    def __unicode__(self):
        return self.path
    
    @property
    def name(self):
        """ File-like attribute (dutck-typing) """
        return self.path
    
    def read(self):
        """ File-like method (dutck-typing) """
        return self.content


class Config(SingletonModel):
    """
    Describes the configuration used for building images
    """
    description = models.CharField(max_length=255)
    version = models.CharField(max_length=64)
    image_name = models.CharField(max_length=255,
        default="firmware-%(node_name)s-%(arch)s-%(version)s-%(build_id)d.img.gz",
        help_text="Image file name. Available variables: %(node_name)s, %(arch)s,"
                  " %(build_id)d, %(version)s")
    
    class Meta:
        verbose_name = "Firmware Config"
        verbose_name_plural = "Firmware Config"
    
    def __unicode__(self):
        return 'Current Firmware Config'
    
    def get_uci(self):
        return self.configuci_set.all().order_by('section')
    
    def eval_uci(self, node, sections=None):
        """ Evaluates all ConfigUCI python expressions """
        uci = []
        config_ucis = self.get_uci()
        if sections is not None:
            config_ucis = config_ucis.filter(section__in=sections)
        for config_uci in config_ucis:
            uci.append({
                'section': config_uci.section,
                'option': config_uci.option,
                'value': config_uci.eval_value(node)})
        return uci
    
    def eval_files(self, node, exclude=[], **kwargs):
        """ Evaluates all ConfigFiles python expressions """
        files = []
        for config_file in self.files.active().exclude(pk__in=exclude):
            files.extend(config_file.get_files(node, files=files, **kwargs))
        return files
    
    def render_uci(self, node, sections=None):
        """ Renders UCI file """
        uci = template.loader.get_template('firmware/uci')
        context = Context({'uci': self.eval_uci(node, sections=sections)})
        return uci.render(context)
    
    def get_image(self, node):
        """
        Returns the correct base image file according to the node architecture
        """
        arch_regex = "(^|,)%s(,|$)" % node.arch
        return self.images.get(architectures__regex=arch_regex).image


class BaseImage(models.Model):
    """
    Describes the image used for generating per node customized images.
    """
    config = models.ForeignKey(Config, related_name='images')
    architectures = MultiSelectField(max_length=250, choices=NODES_NODE_ARCHS)
    image = models.FileField(upload_to=settings.FIRMWARE_DIR,
        help_text='Image file compressed in gzip. The file name must end in .img.gz',
        validators=[validators.RegexValidator('.*\.img\.gz$',
                    'Enter a valid name.', 'invalid')])
    
    def __unicode__(self):
        return ", ".join(self.architectures)
    
    def clean(self):
        """ Prevents repeated architectures """
        #TODO: move this logic to formset validation
        for arch in self.architectures:
            arch_regex = "(^|\s)%s(,|$)" % arch
            try:
                existing = BaseImage.objects.filter(architectures__regex=arch_regex)
            except BaseImage.DoesNotExist:
                pass
            else:
                if existing and (not self.pk or existing[0].pk != self.pk):
                    raise ValidationError("%s already present" % arch)
        super(BaseImage, self).clean()


class ConfigUCI(models.Model):
    """
    UCI options that will be used for generating new images.
    value contains a python code that will be evaluated during the firmware build,
    that way we can get attributes in a dynamic way.
    """
    config = models.ForeignKey(Config)
    section = models.CharField(max_length=32, help_text='UCI config statement',
        default='node')
    option = models.CharField(max_length=32, help_text='UCI option statement')
    value = models.CharField(max_length=255, 
        help_text='Python code that will be evaluated for obtining the value '
                  'from the node. For example: node.properties[\'ip\']')
    
    class Meta:
        verbose_name_plural = "Config UCI"
        unique_together = ['config', 'section', 'option']
    
    def __unicode__(self):
        return "%s.%s" % (self.section, self.option)
    
    def eval_value(self, node):
        """
        Evaluates the 'value' as python code in order to get the current value
        for the given UCI option.
        """
        safe_locals = {'node': node, 'server': Server.objects.get()}
        return unicode(eval(self.value, safe_locals))


class ConfigFileQuerySet(models.query.QuerySet):
    def active(self, **kwargs):
        return self.filter(is_active=True, **kwargs)
    
    def optional(self, **kwargs):
        return self.filter(is_optional=True, **kwargs)


class ConfigFile(models.Model):
    config = models.ForeignKey(Config, related_name='files')
    path = models.CharField(max_length=256)
    content = models.CharField(max_length=256)
    mode = models.CharField(max_length=6, blank=True)
    priority = models.IntegerField(default=0)
    is_optional = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    objects = generate_chainer_manager(ConfigFileQuerySet)
    
    class Meta:
        unique_together = ['config', 'path']
        ordering = ['-priority']
    
    def __unicode__(self):
        return self.path
    
    def get_files(self, node, **kwargs):
        """ Generates all the files related to self ConfigFile """
        safe_locals = kwargs
        safe_locals.update({'node': node,
                            'self': self,
                            'server': Server.objects.get()})
        try:
            paths = eval(self.path, safe_locals)
        except (NameError, SyntaxError):
            paths = eval("self.path", safe_locals)
        
        # get contents
        contents = eval(self.content, safe_locals)
        
        # path and contents can be or not an iterator (multiple files)
        if not hasattr(paths, '__iter__'):
            paths = [paths]
            contents = [contents]
        
        # put all together in a BuildFile list
        files = []
        for path, content in zip(paths, contents):
            f = BuildFile(path=path, content=content, config=self)
            files.append(f)
        return files
    
    @property
    def help_text(self):
        """ Provides help_text file if exists """
        try:
            return self.configfilehelptext.help_text
        except ConfigFileHelpText.DoesNotExist:
            return ''


class ConfigFileHelpText(models.Model):
    config = models.ForeignKey(Config)
    file = models.OneToOneField(ConfigFile)
    help_text = models.TextField()
    
    def __unicode__(self):
        return str(self.file)



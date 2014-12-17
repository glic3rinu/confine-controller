from __future__ import absolute_import

import ast
import logging
import os
import re
from hashlib import sha256

from celery import states as celery_states
from django import template
from django.conf import settings as project_settings
from django.core.exceptions import SuspiciousFileOperation
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.template import Context
from django.utils.functional import cached_property
from django_transaction_signals import defer
from djcelery.models import TaskState
from privatefiles import PrivateFileField

from controller import settings as controller_settings
from controller.core.validators import validate_file_extensions, validate_name
from controller.models.fields import MultiSelectField
from controller.models.utils import generate_chainer_manager
from controller.utils.auth import any_auth_method
from controller.utils.functional import cached
from nodes.models import Node, Server
from nodes.settings import NODES_NODE_ARCHS
from controller.utils.plugins.models import PluginModel
from controller.utils.singletons.models import SingletonModel

from . import settings
from .context import context as eval_context
from .exceptions import ConcurrencyError
from .settings import FIRMWARE_BASE_IMAGE_EXTENSIONS
from .tasks import build as build_task
from .validators import validate_ssh_auth


class BuildQuerySet(models.query.QuerySet):
    def get_current(self, node):
        """ Given an node returns an up-to-date built image, if it exists """
        build = Build.objects.get(node=node)
        if build.state != Build.AVAILABLE: 
            return build
        if build.match_config:
            return build
        else: 
            raise Build.DoesNotExist()


class Build(models.Model):
    """
    Represents a built image for a research device. All the build information
    is copied, not referenced by related objects that can change over time.
    Only the most recent build of each node is stored in order to keep the model simple
    """
    REQUESTED = 'REQUESTED'
    QUEUED = 'QUEUED'
    BUILDING = 'BUILDING'
    AVAILABLE = 'AVAILABLE'
    OUTDATED = 'OUTDATED'
    DELETED = 'DELETED'
    FAILED = 'FAILED'
    
    node = models.OneToOneField('nodes.Node', primary_key=True, related_name='firmware_build')
    date = models.DateTimeField(auto_now_add=True)
    version = models.CharField(max_length=64)
    image = PrivateFileField(storage=settings.FIRMWARE_BUILD_IMAGE_STORAGE,
            upload_to=settings.FIRMWARE_BUILD_IMAGE_PATH, max_length=256,
            condition=any_auth_method(lambda request, self:
                      request.user.has_perm('nodes.getfirmware_node', obj=self.node)))
    base_image = models.FileField(storage=settings.FIRMWARE_BASE_IMAGE_STORAGE,
            upload_to=settings.FIRMWARE_BASE_IMAGE_PATH,
            help_text='Image file compressed in gzip. The file name must end in .img.gz')
    task_id = models.CharField(max_length=36, unique=True, null=True,
            help_text="Celery task ID")
    kwargs = models.TextField()
    
    objects = generate_chainer_manager(BuildQuerySet)
    
    class Meta:
        ordering = ['-date']
    
    def __unicode__(self):
        return unicode(self.node)
    
    def delete(self, *args, **kwargs):
        """ Deletes the build and also the image file stored on the file system """
        super(Build, self).delete(*args, **kwargs)
        try:
            os.remove(self.image.path)
        except:
            pass
    
    @property
    def image_name(self):
        return self.image.name.split('/')[-1]

    @property
    def kwargs_dict(self):
        """ Return stored kwargs as a python dictionary """
        try:
            return ast.literal_eval(self.kwargs)
        except (SyntaxError, ValueError):
            # malformed kwargs string
            return {}

    @property
    @cached
    def db_task(self):
        """ Returns the celery task responsible for 'self' image build """
        if not self.task_id:
            return None
        try:
            return TaskState.objects.get(task_id=self.task_id)
        except TaskState.DoesNotExist:
            return None
    
    @property
    def task(self):
        return build_task.AsyncResult(self.task_id)
    
    @property
    @cached
    def state(self):
        """ Gives the current state of the build """
        if self.image:
            try:
                self.image.file
            except IOError:
                return self.DELETED
            except SuspiciousFileOperation:
                msg = ("There is some issue accessing build image file. Check "
                       "that image.name path is inside image.storage.location.")
                logging.exception(msg)
                return 'ACCESS DENIED'
            else: 
                if self.match_config:
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
    def state_description(self):
        description = {
            Build.REQUESTED: "Building task received.",
            Build.QUEUED: "Building task queued for processing.",
            Build.BUILDING: "Your task is now being processed, this can take a while.",
            Build.AVAILABLE: "Firmware available for download.",
            Build.DELETED: "The firmware is no longer available. Do you want to build a new one?",
            Build.OUTDATED: "The existing firmware is out-dated. Although is "
                            "available to download, maybe you want to delete it "
                            "and build an updated one.",
            Build.FAILED: "The last build has failed. The error logs are monitored "
                          "and this issue will be fixed. But you can try again anyway.",
        }
        return description.get(self.state, '')
    
    @property
    @cached
    def image_sha256(self):
        try:
            return sha256(self.image.file.read()).hexdigest()
        except:
            return None
    
    @classmethod
    def build(cls, node, base_image, async=False, exclude=[], **kwargs):
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
                raise ConcurrencyError("One build at a time.")
            old_build.delete()
        config = Config.objects.get()
        build_obj = Build.objects.create(node=node, version=config.version,
            base_image=base_image.image, kwargs=kwargs)
        
        # handle registry api #245: save cert content into DB
        cert = kwargs.pop('registry_cert')
        config = ConfigFile.objects.get(path='/etc/config/confine')
        build_obj.add_file('/etc/confine/registry-server.crt', cert, config)
        
        if async:
            defer(build_task.delay, build_obj.pk, exclude=exclude, **kwargs)
        else:
            build_obj = build_task(build_obj.pk, exclude=exclude, **kwargs)
        return build_obj
    
    def add_file(self, path, content, config):
        """ Add a new generated file to the build """
        BuildFile.objects.create(build=self, path=path, content=content, config=config)
    
    @cached_property
    def match_config(self):
        """ Checks if a a given build is up-to-date or not """
        # TODO including non-idempotent files (like cryptographyc keys)
        #      will allways evaluate to false
        config = Config.objects.get()
        if self.version != config.version:
            return False
        base_images = [ image.image for image in config.get_images(self.node) ]
        if not self.base_image or self.base_image not in base_images:
            return False
        exclude = list(config.files.optional().values_list('pk', flat=True))
        old_files = self.files.exclude(config__is_optional=True)\
                        .exclude(path='/etc/confine/registry-server.crt')
        old_files = set( (f.path,f.content) for f in old_files )
        new_files = config.eval_files(self.node, exclude=exclude)
        new_files = set( (f.path,f.content) for f in new_files )
        return new_files == old_files


class BuildFile(models.Model):
    """ Describes a file of a built image """
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
        """ File-like attribute (duck-typing) """
        return self.path
    
    def read(self):
        """ File-like method (duck-typing) """
        return self.content


class Config(SingletonModel):
    """ Describes the configuration used for building images """
    description = models.CharField(max_length=255)
    version = models.CharField(max_length=64)
    image_name = models.CharField(max_length=255,
            default="firmware-%(node_name)s-%(arch)s-%(version)s-%(build_id)d.img.gz",
            help_text="Image file name. Available variables: %(node_name)s, %(arch)s,"
                      " %(build_id)d, %(version)s and %(node_id)d")
    
    class Meta:
        verbose_name = "Firmware config"
        verbose_name_plural = "Firmware config"
    
    def __unicode__(self):
        return u'Current Firmware Config'
    
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
        # handle special case of #383 files
        for config_file in self.files.active().exclude(pk__in=exclude):
            try:
                nb_file = node.files.get(path=config_file.path)
            except node.files.model.DoesNotExist:
                # not exists a previous value so cannot be restored
                new_files = config_file.get_files(node, files=files, **kwargs)
                # create or update stored key files
                if config_file.path in NodeKeys.KEY_FILES:
                    node_file, _ = node.files.get_or_create(path=config_file.path)
                    node_file.content = new_files[0].content
                    node_file.save()
            else:
                new_files = [BuildFile(path=nb_file.path, content=nb_file.content, config=config_file)]
            files.extend(new_files)
        return files
    
    def render_uci(self, node, sections=None):
        """ Renders UCI file """
        uci = template.loader.get_template('firmware/uci')
        context = Context({'uci': self.eval_uci(node, sections=sections)})
        return uci.render(context)
    
    def get_images(self, node):
        """ 
        Returns a list of base image files according to the node architecture.
        """
        return self.images.filter_by_arch(node.arch)
    
    def get_image_name(self, node, build=None):
        context = {
            'node_name': node.name,
            'arch': node.arch,
            'build_id': build.pk if build else 0,
            'node_id': node.pk,
            'version': self.version }
        name = self.image_name % context
        return name.replace(' ', '_')


class BaseImageQuerySet(models.query.QuerySet):
    def filter_by_arch(self, arch):
        arch_regex = "(^|,)%s(,|$)" % arch
        return self.filter(architectures__regex=arch_regex)


class BaseImage(models.Model):
    """ Describes the image used for generating per node customized images """
    name = models.CharField(max_length=256, unique=True,
            help_text='Unique name for this base image.A single non-empty line of '
                      'free-form text with no whitespace surrounding it. ',
            validators=[validate_name])
    config = models.ForeignKey(Config, related_name='images')
    architectures = MultiSelectField(max_length=250, choices=NODES_NODE_ARCHS)
    image = models.FileField(storage=settings.FIRMWARE_BASE_IMAGE_STORAGE,
            upload_to=settings.FIRMWARE_BASE_IMAGE_PATH,
            help_text='Image file compressed in gzip. The file name must end in .img.gz',
            validators=[validate_file_extensions(FIRMWARE_BASE_IMAGE_EXTENSIONS)])
    default = models.BooleanField(default=False,
            help_text='If true this base image will be preselected on the firmware '
                      'generation form')
    
    objects = generate_chainer_manager(BaseImageQuerySet)
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.filename)
    
    @property
    def filename(self):
        return os.path.basename(self.image.name)


class ConfigUCI(models.Model):
    """
    UCI options that will be used for generating new images.
    value contains a python code that will be evaluated during the firmware build,
    that way we can get attributes in a dynamic way.
    """
    config = models.ForeignKey(Config)
    section = models.CharField(max_length=32, default='node',
            help_text='UCI config statement')
    option = models.CharField(max_length=32, help_text='UCI option statement')
    value = models.TextField(max_length=255,
            help_text='Python code that will be evaluated for obtining the value '
                      'from the node. I.e. node.properties[\'ip\']')
    
    class Meta:
        verbose_name_plural = "Config UCI"
        unique_together = ['config', 'section', 'option']
        ordering = ['section', 'option']
    
    def __unicode__(self):
        return u"%s.%s" % (self.section, self.option)
    
    def eval_value(self, node):
        """ Evaluates 'value' as python code """
        safe_locals = {'node': node, 'self': self}
        construct_safe_locals.send(sender=type(self), safe_locals=safe_locals)
        return unicode(eval(self.value, safe_locals))


class ConfigFileQuerySet(models.query.QuerySet):
    def active(self, **kwargs):
        return self.filter(is_active=True, **kwargs)
    
    def optional(self, **kwargs):
        return self.filter(is_optional=True, **kwargs)


class ConfigFile(models.Model):
    config = models.ForeignKey(Config, related_name='files')
    path = models.CharField(max_length=256)
    content = models.TextField()
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
        kwargs.update({'node': node, 'self': self})
        construct_safe_locals.send(sender=type(self), safe_locals=safe_locals)
        safe_locals.update(eval_context.get())
        try:
            paths = eval(self.path, safe_locals)
        except (NameError, SyntaxError):
            paths = eval("self.path", safe_locals)
        
        # get contents
        try:
            contents = eval(self.content, safe_locals)
        except IndexError:
            contents = ('Confine-controller firmware generation message: \n'
                'The content of this file depends on another file that is not present')
        
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
    @cached
    def help_text(self):
        """ Provides help_text file if exists """
        try:
            return self.configfilehelptext.help_text
        except ConfigFileHelpText.DoesNotExist:
            return ''


class ConfigFileHelpText(models.Model):
    config = models.ForeignKey(Config)
    file = models.OneToOneField(ConfigFile, related_name='help_text')
    help_text = models.TextField()
    
    def __unicode__(self):
        return unicode(self.help_text)


class ConfigPlugin(PluginModel):
    config = models.ForeignKey(Config, related_name='plugins')


class NodeKeys(models.Model):
    """ Stores node firmware root password and accepted SSH keys. """
    TINC = '/etc/tinc/confine/rsa_key.priv'
    CERT = '/etc/uhttpd.crt.pem'
    PRIVATE = '/etc/uhttpd.key.pem'
    KEY_FILES = [TINC, CERT, PRIVATE]
    
    allow_node_admins = models.BooleanField('Allow current node admins',
            default=True,
            help_text='Enable this option to permanently allow the current '
                      'group and node administrators\' SSH keys to log into '
                      'the node as root.')
    sync_node_admins = models.BooleanField('Synchronize node admins',
            default=False,
            help_text='Enable this option to also allow current or future '
                      'group and node administrators\' SSH keys (as configured '
                      'in the registry) to log into the node as root. '
                      'Please note that this may expose your node to an attack '
                      'if the testbed registry is compromised.')
    ssh_auth = models.TextField('Additional keys', blank=True, null=True,
            help_text='Enter additional SSH keys (in "authorized_keys" format) '
                      'permanently allowed to log into the node as root. '
                      'You may leave the default keys to allow centralized '
                      'maintenance of your node by the controller. Please note '
                      'that this may expose your node to an attack if the '
                      'controller is compromised.',
            validators=[validate_ssh_auth])
    # MD5SUM hashed password in OpenWRT shadow format
    ssh_pass = models.CharField(max_length=128, blank=True, null=True)
    node = models.OneToOneField('nodes.Node', primary_key=True, related_name='keys')
    
    def __unicode__(self):
        return unicode(self.node)
    
    def get_content(self, path):
        try:
            nb_file = self.node.files.get(path=path)
        except NodeBuildFile.DoesNotExist:
            return None
        return nb_file.content
    
    @property
    def tinc(self):
        return self.get_content(NodeKeys.TINC)
    
    @property
    def cert(self):
        return self.get_content(NodeKeys.CERT)
    
    @property
    def private(self):
        return self.get_content(NodeKeys.PRIVATE)


class NodeBuildFile(models.Model):
    """Describes a persistent file of a built image.
    Allows reusing BuildFiles between firmware builds.
    """
    node = models.ForeignKey('nodes.Node', related_name='files')
    path = models.CharField(max_length=256) #XXX replace with ConfigFile.id (foreign key)?
    content = models.TextField()
    
    def __unicode__(self):
        return self.path

    class Meta:
        unique_together = ('node', 'path')
    

# Create OneToOne NodeKeys instance on node creation
# define a dispatch UID for avoid duplicate signals (#505)
@receiver(post_save, sender=Node, dispatch_uid="node_keys")
def create_nodekeys(sender, instance, created, **kwargs):
    if created:
        NodeKeys.objects.create(node=instance)


construct_safe_locals = Signal(providing_args=["instance", "safe_locals"])


@receiver(construct_safe_locals, dispatch_uid="firmware.update_safe_locals")
def update_safe_locals(sender, safe_locals, **kwargs):
    safe_locals.update({'server': Server.objects.first(), 're': re})
    safe_locals.update(dict((setting, getattr(controller_settings, setting))
        for setting in dir(controller_settings) if setting.isupper() ))
    safe_locals.update(dict((setting, getattr(project_settings, setting))
        for setting in dir(project_settings) if setting.isupper() ))


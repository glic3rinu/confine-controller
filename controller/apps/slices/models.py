import hashlib
import os
import tempfile

from django_transaction_signals import defer
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now

from controller.models.fields import MultiSelectField, NullableCharField
from controller.utils import autodiscover
from controller.core.validators import (validate_net_iface_name, validate_prop_name,
        validate_sha256, validate_file_extensions, validate_name)
from nodes.models import Node
from nodes.settings import NODES_NODE_ARCHS

from . import settings
from .exceptions import VlanAllocationError, IfaceAllocationError
from .helpers import save_files_with_pk_value
from .tasks import force_slice_update, force_sliver_update


def get_expires_on():
    """ Used by slice.renew and Slice.expires_on """
    return now() + settings.SLICES_SLICE_EXP_INTERVAL


def clean_sha256(self, fields):
    """
    Check that sha256 has manually provided for an external
    file (specified by uri)
    """
    for field_name in fields:
        if getattr(self, field_name+'_uri') and not getattr(self, field_name+'_sha256'):
            raise ValidationError('Missing %s_sha256.' % field_name)


def clean_uri(self, fields):
    """
    Check if user has provided an uri to override current
    uploaded file and delete the stored one (if any).
    """
    for field_name in fields:
        field = getattr(self, field_name)
        field_uri = getattr(self, field_name + '_uri')
        # allow the API to override uploaded file
        if field and field_uri and field.url != field_uri:
            field.delete()


def set_sha256(self, fields):
    """ Generate sha256 for an uploaded file """
    for field_name in fields:
        field = getattr(self, field_name)
        if field:
            try:
                field.file
            except IOError: # file doesn't exists
                return
            # chunked for avoid memory leak (#428)
            sha256 = hashlib.sha256()
            while True:
                block = field.file.read(2**20) # 1MiB
                if not block:
                    break
                sha256.update(block)
            sha256 = sha256.hexdigest()
            field.file.seek(0)
            setattr(self, field_name + '_sha256', sha256)
        elif not getattr(self, field_name + '_uri'):
            setattr(self, field_name + '_sha256', '')


def set_uri(self, fields):
    """Reset _uri when a file is uploaded"""
    for field_name in fields:
        field = getattr(self, field_name)
        if field:
            try:
                field.file
            except IOError: # file doesn't exists
                return
            setattr(self, field_name + '_uri', '')


def make_upload_to(field_name, base_path, file_name):
    """ dynamically generate file names with randomness for upload_to args """
    def upload_path(instance, filename, base_path=base_path, file_name=file_name,
                    field_name=field_name):
        if not file_name or instance is None:
            return os.path.join(base_path, filename)
        field = type(instance)._meta.get_field_by_name(field_name)[0]
        storage_location = field.storage.base_location
        abs_path = os.path.join(storage_location, base_path)
        splited = filename.split('.')
        context = {
            'pk': instance.pk,
            'original': filename,
            'prefix': splited[0],
            'suffix': splited[1] if len(splited) > 1 else ''
        }
        if '%(rand)s' in file_name:
            prefix, suffix = file_name.split('%(rand)s')
            prefix = prefix % context
            suffix = suffix % context
            with tempfile.NamedTemporaryFile(dir=abs_path, prefix=prefix, suffix=suffix) as f:
                name = f.name.split('/')[-1]
        else:
            name = file_name % context
        name = name.replace(' ', '_')
        return os.path.join(base_path, name)
    return upload_path


class Template(models.Model):
    """
    Describes a template available in the testbed for slices and slivers to use.
    """
    name = models.CharField(max_length=32, unique=True,
            help_text='The unique name of this template. A single line of free-form '
                      'text with no whitespace surrounding it, it can include '
                      'version numbers and other information.',
            validators=[validate_name])
    description = models.TextField(blank=True,
            help_text='An optional free-form textual description of this template.')
    type = models.CharField(max_length=32, choices=settings.SLICES_TEMPLATE_TYPES,
            help_text='The system type of this template. Roughly equivalent to the '
                      'distribution the template is based on, e.g. debian (Debian, '
                      'Ubuntu...), fedora (Fedora, RHEL...), suse (openSUSE, SUSE '
                      'Linux Enterprise...). To instantiate a sliver based on a '
                      'template, the research device must support its type.',
            default=settings.SLICES_TEMPLATE_TYPE_DFLT)
    node_archs = MultiSelectField(max_length=256, choices=NODES_NODE_ARCHS,
            help_text='The node architectures accepted by this template (as reported '
                      'by uname -m, non-empty). Slivers using this template should '
                      'run on nodes whose architecture is listed here.',
            default=settings.SLICES_TEMPLATE_ARCH_DFLT)
    is_active = models.BooleanField(default=True)
    image = models.FileField(help_text="Template's image file.",
            upload_to=make_upload_to('image', settings.SLICES_TEMPLATE_IMAGE_DIR,
                                     settings.SLICES_TEMPLATE_IMAGE_NAME),
            validators=[validate_file_extensions(settings.SLICES_TEMPLATE_IMAGE_EXTENSIONS)])
    image_uri = models.CharField('image URI', max_length=256, blank=True,
            help_text='The URI of this template\'s image file. This member '
                      'cannot be changed if the template is in use. This '
                      'member may be set directly or through the '
                      'do-upload-image controller API function.')
    image_sha256 = models.CharField('image SHA256', max_length=64, blank=True,
            help_text='The SHA256 hash of the previous file, used to check its '
                      'integrity. This member cannot be changed if the '
                      'template is in use. This member may be set directly or '
                      'through the do-upload-image controller API function.',
            validators=[validate_sha256])
    
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.type)
    
    def clean(self):
        super(Template, self).clean()
        clean_sha256(self, ('image',))
    
    def save(self, *args, **kwargs):
        set_sha256(self, ('image',))
        set_uri(self, ('image',))
        super(Template, self).save(*args, **kwargs)


class Slice(models.Model):
    """
    Describes a slice in the testbed. An slice is a set of resources spread over
    several nodes in a testbed which allows researchers to run experiments over it.
    """
    MIN_VLAN_TAG = 0x100
    MAX_VLAN_TAG = 0xfff
    REGISTER = 'register'
    DEPLOY = 'deploy'
    START = 'start'
    STATES = ((REGISTER, 'REGISTER'),
              (DEPLOY, 'DEPLOY'),
              (START, 'START'),)
    
    name = models.CharField(max_length=128, unique=True,
            help_text='A unique name of this slice. A single non-empty line of free-form '
                      'text with no whitespace surrounding it.',
            validators=[validate_name])
    description = models.TextField(blank=True,
            help_text='An optional free-form textual description of this slice.'
                      'e.g. what is being tested, what were the results, '
                      'possible impact of the experiment, URL to related '
                      'resources...')
    expires_on = models.DateField(null=True, blank=True, default=get_expires_on,
            help_text='Expiration date of this slice. Automatically deleted once '
                      'expires.')
    instance_sn = models.PositiveIntegerField(default=0, blank=True,
            help_text='The number of times this slice has been instructed to be reset '
                      '(instance sequence number). Automatically incremented by the '
                      'reset function.',
            verbose_name='instance sequence number')
    allow_isolated = models.BooleanField(default=False,
            help_text='Whether to request a VLAN tag for isolated sliver interfaces '
                      '(see node architecture) at slice deployment time. If the '
                      'allocation is successful, the tag is stored in the '
                      '/isolated_vlan_tag member. Otherwise, the deployment of the '
                      'slice fails',
            verbose_name='Request isolated VLAN tag')
    isolated_vlan_tag = models.IntegerField('Isolated VLAN tag', null=True, blank=True,
            help_text='VLAN tag allocated to this slice. The only values that can '
                      'be set are null which means that no VLAN is wanted for the '
                      'slice, and -1 which asks the server to allocate for the slice '
                      'a new VLAN tag (100 <= vlan_tag < 0xFFF) while the slice is '
                      'instantiated (or active). It cannot be changed on an '
                      'instantiated slice with slivers having isolated interfaces.')
    set_state = models.CharField(max_length=16, choices=STATES, default=REGISTER,
            help_text='The state set on this slice (set state) and its slivers '
                      '(if they do not explicitly indicate a lower one). '
                      'Possible values: register (initial) &lt; deploy &lt; start. '
                      'See <a href="https://wiki.confine-project.eu/arch:'
                      'slice-sliver-states">slice and sliver states</a> for the full '
                      'description of set states and possible transitions.')
    group = models.ForeignKey('users.Group', related_name='slices')
    
    def __unicode__(self):
        return self.name
    
    def update_set_state(self, commit=True):
        if self.set_state in [self.DEPLOY, self.START]:
            if self.isolated_vlan_tag is None and self.allow_isolated:
                try:
                    self.isolated_vlan_tag = Slice._get_vlan_tag()
                except VlanAllocationError:
                    self.set_state = self.REGISTER
        elif self.isolated_vlan_tag > 0: # REGISTER state
            # transition to a register state, deallocating...
            self.isolated_vlan_tag = None
        if commit:
            self.save()
    
    def save(self, *args, **kwargs):
        # TODO send message to user when error happens
        self.update_set_state(commit=False)
        if not self.pk:
            self.expires_on = now() + settings.SLICES_SLICE_EXP_INTERVAL
        super(Slice, self).save(*args, **kwargs)
    
    def clean(self):
        super(Slice, self).clean()
        # clean set_state
        if not self.pk:
            if self.set_state != Slice.REGISTER:
                raise ValidationError("Initial state must be Register")
        # clean allow_isolated
        else:
            old = Slice.objects.get(pk=self.pk)
            has_changed = self.allow_isolated != old.allow_isolated
            if has_changed and old.set_state != self.REGISTER:
                raise ValidationError("Vlan can not be requested in state != register")
    
    def renew(self):
        """Renew expires_on date, except has alreday reached the maximum"""
        new_expires_on = get_expires_on()
        if self.expires_on == new_expires_on.date():
            return False
        self.expires_on = new_expires_on
        self.save()
        return True
    
    def reset(self):
        self.instance_sn += 1
        self.save()
    
    @property
    def max_vlan_nr(self):
        return Slice.MAX_VLAN_TAG
    
    @property
    def min_vlan_nr(self):
        return Slice.MIN_VLAN_TAG
    
    @property
    def vlan_nr(self):
        # backwards-compatibility (#46 note-64)
        if self.set_state != Slice.REGISTER:
            return self.isolated_vlan_tag
        else:
            return -1 if self.allow_isolated else None

    @classmethod
    def _get_vlan_tag(cls):
        qset = cls.objects.exclude(isolated_vlan_tag=None).order_by('-isolated_vlan_tag')
        last_nr = qset.first().isolated_vlan_tag if qset else 0
        if last_nr < cls.MIN_VLAN_TAG:
            return cls.MIN_VLAN_TAG
        if last_nr >= cls.MAX_VLAN_TAG:
            # Try to recycle old values ( very, very ineficient )
            for new_nr in range(cls.MIN_VLAN_TAG, cls.MAX_VLAN_TAG):
                if not cls.objects.filter(isolated_vlan_tag=new_nr).exists():
                    return new_nr
            raise VlanAllocationError("No VLAN address space left.")
        return last_nr + 1
    
    def force_update(self, async=False):
        if async:
            defer(force_slice_update.delay, self.pk)
        else:
            force_slice_update(self.pk)


class SliceProp(models.Model):
    """
    A mapping of (non-empty) arbitrary slice property names to their (string)
    values.
    """
    slice = models.ForeignKey(Slice, related_name='properties')
    name = models.CharField(max_length=64,
            help_text='Per slice unique single line of free-form text with no '
                      'whitespace surrounding it.',
            validators=[validate_prop_name])
    value = models.CharField(max_length=256)
    
    class Meta:
        unique_together = ('slice', 'name')
        verbose_name = 'slice property'
        verbose_name_plural = 'slice properties'
    
    def __unicode__(self):
        return self.name


class SliverDefaults(models.Model):
    """
    Represents the attributes and relations that act as defaults for the
    slivers of a slice.
    """
    slice = models.OneToOneField(Slice, related_name='sliver_defaults')
    instance_sn = models.PositiveIntegerField(default=0, blank=True,
            help_text='The instance sequence number that newly created slivers will '
                      'get. Automatically incremented whenever a sliver of this slice '
                      'is instructed to be updated.',
            verbose_name='New sliver instance sequence number')
    data = models.FileField(blank=True, verbose_name='sliver data',
            upload_to=make_upload_to('data', settings.SLICES_SLICE_DATA_DIR,
                                     settings.SLICES_SLICE_DATA_NAME,),
            help_text='File containing experiment data for slivers (if they do not '
                      'explicitly indicate one)')
    data_uri = NullableCharField('sliver data URI', max_length=256, blank=True,
            null=True,
            help_text='The URI of a file containing sliver data for slivers (if '
                      'they do not explicitly indicate one). Its format and contents '
                      'depend on the type of the template to be used.')
    data_sha256 = NullableCharField('sliver data SHA256', max_length=64,
            blank=True, null=True,
            help_text='The SHA256 hash of the data file, used to check its integrity. '
                      'Compulsory when a file has been specified.',
            validators=[validate_sha256])
    set_state = models.CharField(max_length=16, choices=Slice.STATES, default=Slice.START,
            help_text='The state set by default on its slivers (set state). '
                      'Possible values: register &lt; deploy &lt; start (default). '
                      'See <a href="https://wiki.confine-project.eu/arch:'
                      'slice-sliver-states">slice and sliver states</a> for the full '
                      'description of set states and possible transitions.')
    template = models.ForeignKey(Template, limit_choices_to={'is_active':True},
            help_text='The template to be used by the slivers of this slice (if they '
                      'do not explicitly indicate one).')
    
    class Meta:
        verbose_name_plural = 'sliver defaults'
    
    def __unicode__(self):
        return "%s" % self.slice
    
    def clean(self):
        super(SliverDefaults, self).clean()
        clean_sha256(self, ('data',))
        clean_uri(self, ('data',))
    
    def save(self, *args, **kwargs):
        if not self.pk:
            save_files_with_pk_value(self, ('data',), *args, **kwargs)
        set_sha256(self, ('data',))
        set_uri(self, ('data',))
        super(SliverDefaults, self).save(*args, **kwargs)
    
    # FIXME can be removed when api.aggregate supports nested serializers
    @property
    def slice_resources(self):
        return self.slice.resources
    
    @slice_resources.setter
    def slice_resources(self, value):
        self.slice.resources = value


class Sliver(models.Model):
    """
    Describes a sliver in the testbed, an sliver is a partition of a node's 
    resources assigned to a specific slice.
    """
    slice = models.ForeignKey(Slice, related_name='slivers')
    node = models.ForeignKey(Node, related_name='slivers')
    description = models.TextField(blank=True,
            help_text='An optional free-form textual description of this sliver.')
    instance_sn = models.PositiveIntegerField(default=0, blank=True,
            help_text='The number of times this sliver has been instructed to be '
                      'updated (instance sequence number).',
            verbose_name='instance sequence number')
    data = models.FileField(blank=True, verbose_name='sliver data',
            upload_to=make_upload_to('data', settings.SLICES_SLIVER_DATA_DIR,
                                     settings.SLICES_SLIVER_DATA_NAME),
            help_text='File containing data for this sliver.')
    data_uri = NullableCharField('sliver data URI', max_length=256, blank=True,
            null=True,
            help_text='If present, the URI of a file containing data for '
                      'this sliver, instead of the one specified by the slice. Its '
                      'format and contents depend on the type of the template to be used.')
    data_sha256 = NullableCharField('sliver data SHA256', max_length=64,
            blank=True, null=True,
            help_text='The SHA256 hash of the sliver data file, used to check its integrity. '
                      'Compulsory when a file has been specified.',
            validators=[validate_sha256])
    set_state = NullableCharField(max_length=16, choices=Slice.STATES, blank=True,
            help_text='If present, the state set on this sliver (set state), '
                      'which overrides a higher one specified by the slice '
                      '(e.g. register overrides start, but start does not override register). '
                      'Possible values: register (initial) &lt; deploy &lt; start. '
                      'See <a href="https://wiki.confine-project.eu/arch:'
                      'slice-sliver-states">slice and sliver states</a> for the full '
                      'description of set states and possible transitions.', null=True)
    template = models.ForeignKey(Template, null=True, blank=True,
            limit_choices_to={'is_active':True},
            help_text='If present, the template to be used by this sliver, instead '
                      'of the one specified by the slice.')
    
    _iface_registry = {}
    
    class Meta:
        unique_together = ('slice', 'node')
    
    def __unicode__(self):
        return u'%s@%s' % (self.slice.name, self.node.name)
    
    def clean(self):
        super(Sliver, self).clean()
        clean_sha256(self, ('data',))
        clean_uri(self, ('data',))
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.instance_sn = self.slice.sliver_defaults.instance_sn
            save_files_with_pk_value(self, ('data',), *args, **kwargs)
        set_sha256(self, ('data',))
        set_uri(self, ('data',))
        super(Sliver, self).save(*args, **kwargs)
    
    @property
    def max_num_ifaces(self):
        return 256 # limited by design -> #nr: unsigned 8 bits
    
    @property
    def effective_set_state(self):
        slice = self.slice
        # sliver set_state overrides sliver_defaults
        set_state = self.set_state or slice.sliver_defaults.set_state
        # effective set_state <= slice.set_state
        if slice.set_state == slice.DEPLOY and set_state == slice.REGISTER:
            return set_state
        elif slice.set_state == slice.START and set_state in [slice.REGISTER, slice.DEPLOY]:
            return set_state
        return slice.set_state
    
    @property
    def mgmt_iface(self):
        iface = self.interfaces.filter(type='management')
        return iface.first() if iface else None
    
    @property
    def mgmt_net(self):
        """
        Only available if the sliver has interfaces of type management,
        in which case the management address is that of the first
        management interface, with "native" as a backend. Otherwise
        the whole member is null.
        """
        if self.mgmt_iface is None:
            return None
        return {
            "backend": "native",
            "addr": self.mgmt_iface.ipv6_addr,
            # keep for backwards compatibility (see #450 note 15)
            "address": self.mgmt_iface.ipv6_addr
        }

    @property
    def api_id(self):
        """ The unique ID of this sliver (REST-API) """
        return "%i@%i" % (self.slice_id, self.node_id)
    
    def update(self):
        self.instance_sn += 1
        self.save()
        self.slice.sliver_defaults.instance_sn += 1
        self.slice.sliver_defaults.save()
    
    def force_update(self, async=False):
        if async:
            defer(force_sliver_update.delay, self.pk)
        else:
            force_sliver_update(self.pk)
    
    @classmethod
    def register_iface(cls, iface, name):
        """ Stores iface in { 'iface_type': iface_object } format """
        if name not in settings.SLICES_DISABLED_SLIVER_IFACES:
            cls._iface_registry[name] = iface()
    
    @classmethod
    def get_registered_ifaces(cls):
        """ Returns {'iface_type': iface_object} with registered ifaces """
        return cls._iface_registry


class SliverProp(models.Model):
    """
    A mapping of (non-empty) arbitrary sliver property names to their (string)
    values.
    """
    sliver = models.ForeignKey(Sliver, related_name='properties')
    name = models.CharField(max_length=64,
            help_text='Per slice unique single line of free-form text with no '
                      'whitespace surrounding it',
            validators=[validate_prop_name])
    value = models.CharField(max_length=256)
    
    class Meta:
        unique_together = ('sliver', 'name')
        verbose_name = 'sliver property'
        verbose_name_plural = 'sliver properties'
    
    def __unicode__(self):
        return self.name


# Autodiscover sliver ifaces
autodiscover('ifaces')
IFACE_TYPE_CHOICES = tuple(
    (name, name.capitalize()) for name in Sliver.get_registered_ifaces() )


class SliverIface(models.Model):
    """
    Implememts the network interfaces that will be created in the slivers.
    There must exist a first interface of type private. See node architecture.
    """
    sliver = models.ForeignKey(Sliver, related_name='interfaces')
    nr = models.PositiveIntegerField('number',
            help_text='The unique 8-bit, positive integer number of this interface '
                      'in this sliver. Interface #0 is always the private interface.')
    name = models.CharField(max_length=10,
            help_text='The name of this interface. It must match the regular '
                      'expression ^[a-z]+[0-9]*$ and have no more than 10 characters.',
            validators=[validate_net_iface_name])
    type = models.CharField(max_length=16, choices=IFACE_TYPE_CHOICES,
            help_text="The type of this interface. Types public4 and public6 are only "
                      "available if the node's sliver_pub_ipv4 and sliver_pub_ipv6 "
                      "respectively are not none. There can only be one interface of "
                      "type private, and by default it is configured for both IP4 and "
                      "IPv6 default routes using the RD's internal addresses. The "
                      "first public4 interface declared is configured for the default "
                      "IPv4 route using the CD's IPv4 gateway address, and similarly "
                      "with public6 interfaces for IPv6.")
    parent = models.ForeignKey('nodes.DirectIface', null=True, blank=True,
            help_text="The name of a direct interface in the research device to use "
                      "for this interface's traffic (VLAN-tagged); the slice must "
                      "have a non-null isolated_vlan_tag. Only meaningful (and "
                      "mandatory) for isolated interfaces.")
    
    class Meta:
        unique_together = ('sliver', 'name')
        verbose_name = 'sliver interface'
        verbose_name_plural = 'sliver interfaces'
    
    def __unicode__(self):
        return self.name
    
    def clean(self):
        super(SliverIface, self).clean()
        if self.type:
            Sliver.get_registered_ifaces()[self.type].clean_model(self)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.nr = self._get_nr()
        super(SliverIface, self).save(*args, **kwargs)
    
    @property
    def parent_name(self):
        return self.parent.name if self.parent else None
    
    @property
    def max_nr(self):
        return 256
    
    @property
    def ipv6_addr(self):
        """
        Returns IPv6 address of the SliverIfaces that works on L3.
        Notice that not all L3 ifaces has a predictable IPv6 address, thus might
        depend on the node state which is unknown by the server.
        """
        if self.type == '':
            return None
        return Sliver.get_registered_ifaces()[self.type].ipv6_addr(self)
    
    @property
    def ipv4_addr(self):
        """
        Returns the IPv4 address of the SliverIfaces that works on L3.
        Notice that not all L3 ifaces has a predictable IPv6 address, thus might
        depend on the node state which is unknown by the server.
        """
        if self.type == '':
            return None
        return Sliver.get_registered_ifaces()[self.type].ipv4_addr(self)
    
    def _get_nr(self):
        """ Calculates nr value of the new SliverIface """
        iface = Sliver.get_registered_ifaces()[self.type]
        # first check if iface has defined its own _get_nr()
        if hasattr(iface, '_get_nr'):
            return iface._get_nr(self)
        # TODO use sliver_pub_ipv{4,6}_range/avail/total for PUBLIC{4,6}
        if not SliverIface.objects.filter(sliver=self.sliver).exists():
            return 1
        last_nr = SliverIface.objects.filter(sliver=self.sliver).order_by('-nr').first().nr
        if last_nr >= self.max_nr:
            # try to recycle old values
            for new_nr in range(1, self.max_nr):
                if not Slice.objects.filter(sliver=self.sliver, isolated_vlan_tag=new_nr).exists():
                    return new_nr
            raise IfaceAllocationError("No Iface NR space left.")
        return last_nr + 1

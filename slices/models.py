from datetime import datetime
from hashlib import sha256

from django_transaction_signals import defer
from django.conf import settings as project_settings
from django.contrib.auth import get_user_model
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models
from IPy import IP
from private_files import PrivateFileField

from common.fields import MultiSelectField
from common.ip import lsb, msb, int_to_hex_str
from common.utils import autodiscover
from common.validators import validate_net_iface_name, validate_prop_name
from nodes.models import Node

from . import settings
from .tasks import force_slice_update, force_sliver_update


private_storage = FileSystemStorage(location=project_settings.PRIVATE_MEDIA_ROOT)


def get_expires_on():
    """ Used by slice.renew and Slice.expires_on """
    return datetime.now() + settings.SLICES_SLICE_EXP_INTERVAL


class Template(models.Model):
    """
    Describes a template available in the testbed for slices and slivers to use.
    """
    name = models.CharField(max_length=32, unique=True, 
        help_text='The unique name of this template. A single line of free-form '
                  'text with no whitespace surrounding it, it can include '
                  'version numbers and other information.',
        validators=[validators.RegexValidator('^[a-z][_0-9a-z]*[0-9a-z]$', 
                   'Enter a valid name.', 'invalid')])
    description = models.TextField(blank=True, 
        help_text='An optional free-form textual description of this template.')
    type = models.CharField(max_length=32, choices=settings.SLICES_TEMPLATE_TYPES,
        help_text='The system type of this template. Roughly equivalent to the '
                  'distribution the template is based on, e.g. debian (Debian, '
                  'Ubuntu...), fedora (Fedora, RHEL...), suse (openSUSE, SUSE '
                  'Linux Enterprise...). To instantiate a sliver based on a '
                  'template, the research device must support its type.',
        default=settings.SLICES_TEMPLATE_TYPE_DFLT)
    node_archs = MultiSelectField(max_length=32, choices=settings.SLICES_TEMPLATE_ARCHS,
        help_text='The node architectures accepted by this template (as reported '
                  'by uname -m, non-empty). Slivers using this template should '
                  'run on nodes whose architecture is listed here.')
    is_active = models.BooleanField(default=True)
    image = models.FileField(upload_to=settings.SLICES_TEMPLATE_IMAGE_DIR, 
        help_text='Template\'s image file.')
    
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.type)
    
    @property
    def image_sha256(self):
        try: return sha256(self.image.file.read()).hexdigest()
        except: return None


class Slice(models.Model):
    """
    Describes a slice in the testbed. An slice is a set of resources spread over
    several nodes in a testbed which allows researchers to run experiments over it.
    """
    REGISTER = 'register'
    INSTANTIATE = 'instantiate'
    ACTIVATE = 'activate'
    STATES = ((REGISTER, 'Register'),
              (INSTANTIATE, 'Instantiate'),
              (ACTIVATE, 'Activate'),)
    
    name = models.CharField(max_length=64, unique=True, 
        help_text='A unique name for this slice matching the regular expression'
                  '^[a-z][_0-9a-z]*[0-9a-z]$', 
        validators=[validators.RegexValidator('^[a-z][_0-9a-z]*[0-9a-z]$', 
                   'Enter a valid name.', 'invalid')])
    description = models.TextField(blank=True, 
        help_text='An optional free-form textual description of this slice.')
    expires_on = models.DateField(null=True, blank=True, 
        default=get_expires_on,
        help_text='Expiration date of this slice. Automatically deleted once '
                  'expires.')
    instance_sn = models.PositiveIntegerField(default=0, blank=True, 
        help_text='Number of times this slice has been instructed to be reset '
                  '(instance sequence number).', 
        verbose_name='Instanse Sequence Number')
    new_sliver_instance_sn = models.PositiveIntegerField(default=0, blank=True, 
        help_text='Instance sequence number for newly created slivers.',
        verbose_name='New Sliver Instance Sequence Number')
    vlan_nr = models.IntegerField('VLAN Number', null=True, blank=True,
        help_text='VLAN number allocated to this slice. The only values that can '
                  'be set are null which means that no VLAN is wanted for the '
                  'slice, and -1 which asks the server to allocate for the slice '
                  'a new VLAN number (2 <= vlan_nr < 0xFFF) while the slice is '
                  'instantiated (or active). It cannot be changed on an '
                  'instantiated slice with slivers having isolated interfaces.')
    exp_data = PrivateFileField(blank=True, upload_to=settings.SLICES_SLICE_EXP_DATA_DIR, 
        storage=private_storage, verbose_name='Experiment Data',
        condition=lambda request, self: 
                  request.user.has_perm('slices.slice_change', obj=self),
        help_text='.tar.gz archive containing experiment data for slivers (if '
                  'they do not explicitly indicate one)', 
        validators=[validators.RegexValidator('.*\.tar\.gz', 
                   'Upload a valid .tar.gz file', 'invalid')],)
    set_state = models.CharField(max_length=16, choices=STATES, default=REGISTER)
    template = models.ForeignKey(Template, 
        help_text='The template to be used by the slivers of this slice (if they '
                  'do not explicitly indicate one).')
    group = models.ForeignKey('users.Group')
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # FIXME prevent modifications on vlan_nr once is seted
        if self.vlan_nr == -1:
            if self.set_state == self.INSTANTIATE:
                self.vlan_nr = self._get_vlan_nr()
            elif not self.set_state == self.REGISTER:
                raise self.VlanAllocationError('This value can not be setted')
        if not self.pk:
            self.expires_on = datetime.now() + settings.SLICES_SLICE_EXP_INTERVAL
        super(Slice, self).save(*args, **kwargs)
    
    @property
    def slivers(self):
        return self.sliver_set.all()
    
    @property
    def properties(self):
        return dict(self.sliceprop_set.all().values_list('name', 'value'))
    
    @property
    def exp_data_sha256(self):
        try: return sha256(self.exp_data.file.read()).hexdigest()
        except: return None
    
    def renew(self):
        self.expires_on = get_expires_on()
        self.save()
    
    def reset(self):
        self.instance_sn += 1
        self.save()
    
    @property
    def max_vlan_nr(self):
        return int('ffff', 16)
    
    def _get_vlan_nr(self):
        last_nr = Slice.objects.order_by('-vlan_nr')[0].vlan_nr
        if last_nr < 2: return 2
        if last_nr >= self.max_vlan_nr:
            # Try to recycle old values
            for new_nr in range(2, self.max_vlan_nr):
                if not Slice.objects.filter(vlan_nr=new_nr).exists():
                    return new_nr
            raise self.VlanAllocationError("No VLAN address space left.")
        return last_nr + 1
    
    def force_update(self, async=False):
        if async: defer(force_slice_update.delay, self.pk)
        else: force_slice_update(self.pk)
    
    class VlanAllocationError(Exception): pass


class SliceProp(models.Model):
    """
    A mapping of (non-empty) arbitrary slice property names to their (string) 
    values.
    """
    slice = models.ForeignKey(Slice)
    name = models.CharField(max_length=64,
        help_text='Per slice unique single line of free-form text with no '
                  'whitespace surrounding it.',
        validators=[validate_prop_name])
    value = models.CharField(max_length=256)
    
    class Meta:
        unique_together = ('slice', 'name')
        verbose_name = 'Slice Property'
        verbose_name_plural = 'Slice Properties'
    
    def __unicode__(self):
        return self.name


class Sliver(models.Model):
    """
    Describes a sliver in the testbed, an sliver is a partition of a node's 
    resources assigned to a specific slice.
    """
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey(Node)
    description = models.TextField(blank=True, 
        help_text='An optional free-form textual description of this sliver.')
    instance_sn = models.PositiveIntegerField(default=0, blank=True,
        help_text='The number of times this sliver has been instructed to be '
                  'reset (instance sequence number).', 
        verbose_name='Instance Sequence Number')
    exp_data = PrivateFileField(blank=True, upload_to=settings.SLICES_SLICE_EXP_DATA_DIR, 
        storage=private_storage, verbose_name='Experiment Data',
        condition=lambda request, self: request.user.has_perm('slices.sliver_change', obj=self),
        help_text='.tar.gz archive containing experiment data for this sliver.',
        validators=[validators.RegexValidator('.*\.tar\.gz', 
                   'Upload a valid .tar.gz file', 'invalid')],)
    template = models.ForeignKey(Template, null=True, blank=True, 
        help_text='If present, the template to be used by this sliver, instead '
                  'of the one specified by the slice.')
    
    _iface_registry = {}
    
    class Meta:
        unique_together = ('slice', 'node')
    
    def __unicode__(self):
        return "%s@%s" % (self.slice.name, self.node.name)
    
    @property
    def nr(self):
        return self.pk # TODO use automatic id? generate?
    
    @property
    def exp_data_sha256(self):
        try: return sha256(self.exp_data.file.read()).hexdigest()
        except: return None
    
    @property
    def exp_data_sha256(self):
        try: return sha256(self.exp_data.file.read()).hexdigest()
        except: return None
    
    @property
    def properties(self):
        return dict(self.sliverprop_set.all().values_list('name', 'value'))
    
    @property
    def interfaces(self):
        return self.sliveriface_set.all()
    
    @property
    def max_num_ifaces(self):
        return 256 #limited by design -> #nr: unsigned 8 bits
    
    def reset(self):
        self.instance_sn += 1
        self.save()
    
    def force_update(self, async=False):
        # TODO rename to pull request?
        if async: defer(force_sliver_update.delay, self.pk)
        else: force_sliver_update(self.pk)
    
    @classmethod
    def register_iface(cls, iface, name):
        if name not in settings.SLICES_DISABLED_SLIVER_IFACES:
            cls._iface_registry[name] = iface()
    
    @classmethod
    def get_registred_iface_types(cls):
        types = cls._iface_registry.keys() 
        return zip(types, [ iface.capitalize() for iface in types ])
    
    @classmethod
    def get_registred_iface_type(cls, iface):
        # TODO inspect class/object and act upon it
        for k, v in cls._iface_registry.iteritems():
            if type(v) is iface: return k
    
    @classmethod
    def get_registred_iface(cls, type_):
        return cls._iface_registry[type_]
    
    @classmethod
    def get_registred_ifaces(cls):
        return cls._iface_registry.values()


class SliverProp(models.Model):
    """
    A mapping of (non-empty) arbitrary sliver property names to their (string) 
    values.
    """
    sliver = models.ForeignKey(Sliver)
    name = models.CharField(max_length=64,
        help_text='Per slice unique single line of free-form text with no '
                  'whitespace surrounding it',
        validators=[validate_prop_name])
    value = models.CharField(max_length=256)
    
    class Meta:
        unique_together = ('sliver', 'name')
        verbose_name = 'Sliver Property'
        verbose_name_plural = 'Sliver Properties'
    
    def __unicode__(self):
        return self.name


# Autodiscover sliver ifaces
# Done just before entering to the SliverIface definition because we want 
# type(choices=Sliver.get_registred_iface_types...) to be properly filled
autodiscover('ifaces')


class SliverIface(models.Model):
    """
    Implememts the network interfaces that will be created in the slivers.
    There must exist a first interface of type private. See node architecture.
    """
    # TODO: precreate a private interface
    sliver = models.ForeignKey(Sliver)
    nr = models.PositiveIntegerField('Number',
        help_text='The unique 8-bit, positive integer number of this interface '
                  'in this sliver. Interface #0 is always the private interface.')
    name = models.CharField(max_length=10,
        help_text='The name of this interface. It must match the regular '
                  'expression ^[a-z]+[0-9]*$ and have no more than 10 characters.',
        validators=[validate_net_iface_name])
    type = models.CharField(max_length=16, choices=Sliver.get_registred_iface_types(),
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
                  "have a non-null vlan_nr. Only meaningful (and mandatory) for "
                  "isolated interfaces.")
    
    class Meta:
        unique_together = ('sliver', 'name')
        ordering = ['nr']
        verbose_name = 'Sliver Interface'
        verbose_name_plural = 'Sliver Interfaces'
    
    def __unicode__(self):
        return self.name
    
    def clean(self):
        super(SliverIface, self).clean()
        if self.type:
            Sliver.get_registred_iface(self.type).clean_model(self)
    
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
        return Sliver.get_registred_iface(self.type).ipv6_addr(self)
    
    @property
    def ipv4_addr(self):
        """
        Returns the IPv4 address of the SliverIfaces that works on L3.
        Notice that not all L3 ifaces has a predictable IPv6 address, thus might
        depend on the node state which is unknown by the server.
        """
        if self.type == '':
            return None
        return Sliver.get_registred_iface(self.type).ipv4_addr(self)
    
    @property
    def mac_addr(self):
        """
        Expected address calculated in the server (can be different from the
        one showed in the node, which is the real address)
        
        <mac-prefix-msb>:<mac-prefix-lsb>:<node-id-msb>:<node-id-lsb>:<sliver-n>:<interface-n>
            example 06:ab:04:d2:05:00
        """
        node = self.parent.node
        node_id = int_to_hex_str(node.id, 4)
        mac_prefix = node.get_sliver_mac_prefix()
        words = [
            msb(mac_prefix),
            lsb(mac_prefix),
            msb(node_id),
            lsb(node_id),
            int_to_hex_str(self.sliver.nr, 2),
            int_to_hex_str(self.nr, 2)]
        return ':'.join(words)
    
    def _get_nr(self):
        """ Calculates nr value of the new SliverIface """
        iface = Sliver.get_registred_iface(self.type)
        # first check if iface has defined its own _get_nr()
        if hasattr(iface, '_get_nr'):
            return iface._get_nr(self)
        # TODO use sliver_pub_ipv{4,6}_range/avail/total for PUBLIC{4,6}
        if not SliverIface.objects.filter(sliver=self.sliver).exists():
            return 1
        last_nr = SliverIface.objects.filter(sliver=self.sliver).order_by('-nr')[0].nr
        if last_nr >= self.max_nr:
            # try to recycle old values
            for new_nr in range(1, self.max_nr):
                if not Slice.objects.filter(sliver=self.sliver, vlan_nr=new_nr).exists():
                    return new_nr
            raise self.IfaceAllocationError("No Iface NR space left.")
        return last_nr + 1
    
    class StateNotAvailable(Exception): pass
    
    class IfaceAllocationError(Exception): pass

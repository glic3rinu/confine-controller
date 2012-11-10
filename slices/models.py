from datetime import datetime
from django_extensions.db import fields
from django_transaction_signals import defer
from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from hashlib import sha256
from nodes.models import Node
from slices import settings
from slices.tasks import force_slice_update, force_sliver_update
import re


# TODO protect exp_data and data files (like in firmware.build.image)

class Template(models.Model):
    """
    Describes a template available in the testbed for slices and slivers to use.
    """
    name = models.CharField(max_length=32, unique=True, 
        help_text='The unique name of this template. A single line of free-form'
                  ' text with no whitespace surrounding it, it can include '
                  'version numbers and other information.',
        validators=[validators.RegexValidator(re.compile('^[a-z][_0-9a-z]*[0-9a-z]$.'), 
                   'Enter a valid name.', 'invalid')])
    description = models.TextField(blank=True, 
        help_text='An optional free-form textual description of this template.')
    type = models.CharField(max_length=32, choices=settings.TEMPLATE_TYPES,
        help_text='The system type of this template. Roughly equivalent to the '
                  'distribution the template is based on, e.g. debian (Debian, '
                  'Ubuntu...), fedora (Fedora, RHEL...), suse (openSUSE, SUSE '
                  'Linux Enterprise...). To instantiate a sliver based on a '
                  'template, the research device must support its type.',
        default=settings.DEFAULT_TEMPLATE_TYPE)
    arch = models.CharField(max_length=32, verbose_name='Architecture', 
        choices=settings.TEMPLATE_ARCHS, default=settings.DEFAULT_TEMPLATE_ARCH,
        help_text='Architecture of this template (as reported by uname -m). '
                  'Slivers using this template should run on nodes that match '
                  'this architecture.')
    is_active = models.BooleanField(default=True)
    data = models.FileField(upload_to=settings.TEMPLATE_DATA_DIR, 
        help_text='Template\'s image file.')
    
    def __unicode__(self):
        return self.name
    
    @property
    def data_sha256(self):
        try: return sha256(self.data.file.read()).hexdigest()
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
                  '^[a-z][_0-9a-z]*[0-9a-z]$.', 
        validators=[validators.RegexValidator(re.compile('^[a-z][_0-9a-z]*[0-9a-z]$.'), 
                   'Enter a valid name.', 'invalid')])
    uuid = fields.UUIDField(auto=True, unique=True)
    pubkey = models.TextField(null=True, blank=True, verbose_name='Public Key',
        help_text='PEM-encoded RSA public key for this slice (used by SFA).')
    description = models.TextField(blank=True, 
        help_text='An optional free-form textual description of this slice.')
    expires_on = models.DateField(null=True, blank=True, 
        default=lambda:datetime.now() + settings.SLICE_EXPIRATION_INTERVAL,
        help_text='Expiration date of this slice. Automatically deleted once '
                  'expires.')
    instance_sn = models.PositiveIntegerField(default=0, blank=True, 
        help_text='Number of times this slice has been instructed to be reset '
                  '(instance sequence number).', 
        verbose_name='Instanse Sequence Number')
    new_sliver_instance_sn = models.PositiveIntegerField(default=0, blank=True, 
        help_text='Instance sequence number for newly created slivers.',
        verbose_name='New Sliver Instance Sequence Number')
    # TODO: implement what vlan_nr.help_text says.
    vlan_nr = models.IntegerField(null=True, blank=True, verbose_name='VLAN Number'
        help_text='VLAN number allocated to this slice. The only values that can'
                  ' be set are null which means that no VLAN is wanted for the '
                  'slice, and -1 which asks the server to allocate for the slice'
                  ' a new VLAN number (2 <= vlan_nr < 0xFFF) while the slice is '
                  'instantiated (or active). It cannot be changed on an '
                  'instantiated slice with slivers having isolated interfaces.')
    exp_data = models.FileField(blank=True, upload_to=settings.SLICE_EXP_DATA_DIR,
        help_text='.tar.gz archive containing experiment data for slivers (if'
                  'they do not explicitly indicate one)', 
        validators=[validators.RegexValidator(re.compile('.*\.tar\.gz'), 
                   'Upload a valid .tar.gz file', 'invalid')],
        verbose_name='Experiment Data')
    set_state = models.CharField(max_length=16, choices=STATES, default=REGISTER)
    template = models.ForeignKey(Template, 
        help_text='The template to be used by the slivers of this slice (if they'
                  ' do not explicitly indicate one).')
    users = models.ManyToManyField(User,
        help_text='A list of users able to login as root in slivers using their '
                  'authentication tokens (usually an SSH key).')
    
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
            self.expires_on = datetime.now() + settings.SLICE_EXPIRATION_INTERVAL
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
    
    def _get_vlan_nr(self):
        last_nr = Slice.objects.order_by('-vlan_nr')[0]
        if last_nr < 2: return 2
        if last_nr >= int('FFFF', 16):
            for new_nr in range(2, int('FFFF', 16)):
                if not Slice.objects.filter(vlan_nr=new_nr):
                    return new_nr
            raise self.VlanAllocationError("No VLAN address space left")
        return last_nr + 1
    
    class VlanAllocationError(Exception): pass
    
    def force_update(self, async=False):
        if async: defer(force_slice_update.delay, self.pk)
        else: force_slice_update(self.pk)


class SliceProp(models.Model):
    """
    A mapping of (non-empty) arbitrary slice property names to their (string) 
    values.
    """
    slice = models.ForeignKey(Slice)
    name = models.CharField(max_length=64)
    value = models.CharField(max_length=256)
    
    class Meta:
        unique_together = ('slice', 'name')
    
    def __unicode__(self):
        return self.name


class Sliver(models.Model):
    """
    Describes a sliver in the testbed, an sliver is a partition of a node's 
    resources assigned to a specific slice.
    """
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey(Node)
    description = models.CharField(max_length=256, blank=True, 
        help_text='An optional free-form textual description of this sliver.')
    instance_sn = models.PositiveIntegerField(default=0, blank=True,
        help_text='The number of times this sliver has been instructed to be '
                  'reset (instance sequence number).', 
        verbose_name='Instance Sequence Number')
    exp_data = models.FileField(blank=True, upload_to=settings.SLICE_EXP_DATA_DIR,
        help_text='.tar.gz archive containing experiment data for this sliver.',
        validators=[validators.RegexValidator(re.compile('.*\.tar\.gz'), 
                   'Upload a valid .tar.gz file', 'invalid')],
        verbose_name='Experiment Data',)
    template = models.ForeignKey(Template, null=True, blank=True, 
        help_text='If present, the template to be used by this sliver, instead '
                  'of the one specified by the slice.')
    
    def __unicode__(self):
        return self.description if self.description else str(self.id)
    
    @property
    def exp_data_sha256(self):
        try: return sha256(self.exp_data.file.read()).hexdigest()
        except: return None
    
    @property
    def properties(self):
        return dict(self.sliverprop_set.all().values_list('name', 'value'))
    
    @property
    def interfaces(self):
        try: ifaces = [self.privateiface] 
        except PrivateIface.DoesNotExist: ifaces = []
        ifaces += list(self.publiciface_set.all())
        ifaces += list(self.isolatediface_set.all())
        return ifaces
    
    def reset(self):
        self.instance_sn += 1
        self.save()
    
    def force_update(self, async=False):
        if async: defer(force_sliver_update.delay, self.pk)
        else: force_sliver_update(self.pk)


class SliverProp(models.Model):
    """
    A mapping of (non-empty) arbitrary sliver property names to their (string) 
    values.
    """
    sliver = models.ForeignKey(Sliver)
    name = models.CharField(max_length=64)
    value = models.CharField(max_length=256)
    
    class Meta:
        unique_together = ('sliver', 'name')
    
    def __unicode__(self):
        return self.name


class SliverIface(models.Model):
    """
    Base class for sliver network interfaces
    """
    name = models.CharField(max_length=16)
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return str(self.pk)
    
    @property
    def type(self):
        return self._meta.verbose_name.split(' ')[0]
    
    @property
    def parent_name(self):
        if hasattr(self, 'parent'): 
            return self.parent.name
        return None


class IsolatedIface(SliverIface):
    """
    Describes an Isolated interface of an sliver: It is used for sharing the 
    same physical interface but isolated at L3, by means of tagging all the 
    outgoing traffic with a VLAN tag per slice. By means of using an isolated 
    interface, the researcher will be able to configure it at L3, but several 
    slices may share the same physical interface.
    """
    sliver = models.ForeignKey(Sliver)
    parent = models.ForeignKey('nodes.DirectIface', unique=True)
    
    class Meta:
        unique_together = ['sliver', 'parent']
    
    @property
    def use_default_gw(self):
        return None


class IpSliverIface(SliverIface):
    """
    Base class for IP based sliver interfaces. IP Interfaces might have assigned
    either a public or a private address.
    """
    use_default_gw = models.BooleanField(default=True, 
        help_text='Whether to use a host (provided by the research device) in '
                  'the network connected to this interface as a default gateway.', 
        verbose_name='Use Default Gateway')
    
    class Meta:
        abstract = True


class PublicIface(IpSliverIface):
    """
    Describes a Public Interface for an sliver. Traffic from a public interface 
    will be bridged to the community network.
    """
    sliver = models.ForeignKey(Sliver)


class PrivateIface(IpSliverIface):
    """
    Describes a Private Interface of an sliver.Traffic from a private interface 
    will be forwarded to the community network by means of NAT. Every sliver 
    will have at least a private interface.
    """
    sliver = models.OneToOneField(Sliver)



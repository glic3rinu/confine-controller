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

def get_expires_on():
    return datetime.now() + settings.SLICE_EXPIRATION_INTERVAL


class Template(models.Model):
    name = models.CharField(max_length=32, unique=True, help_text="""The unique
        name of this template. A single line of free-form text with no whitespace
        surrounding it, it can include version numbers and other information.""",
        validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'), 
            'Enter a valid name.', 'invalid')])
    description = models.TextField(blank=True, help_text="""An optional free-form
        textual description of this template.""")
    type = models.CharField(max_length=32, choices=settings.TEMPLATE_TYPES,
        default=settings.DEFAULT_TEMPLATE_TYPE, help_text="""The system type of
        this template. Roughly equivalent to the distribution the template is 
        based on, e.g. debian (Debian, Ubuntu...), fedora (Fedora, RHEL...), suse
        (openSUSE, SUSE Linux Enterprise...). To instantiate a sliver based on a
        template, the research device must support its type.""")
    arch = models.CharField(verbose_name="Architecture", max_length=32, 
        choices=settings.TEMPLATE_ARCHS, default=settings.DEFAULT_TEMPLATE_ARCH,
        help_text="""The architecture of this template (as reported by uname -m).
            Slivers using this template should run on nodes that match this 
            architecture.""")
    is_active = models.BooleanField(default=True)
    data = models.FileField(upload_to=settings.TEMPLATE_DATA_DIR, help_text="""
        template's image file.""")
    
    def __unicode__(self):
        return self.name
    
    @property
    def data_sha256(self):
        try: return sha256(self.data.file.read()).hexdigest()
        except: return None


class Slice(models.Model):
    REGISTER = 'register'
    INSTANTIATE = 'instantiate'
    ACTIVATE = 'activate'
    STATES = ((REGISTER, 'Register'),
              (INSTANTIATE, 'Instantiate'),
              (ACTIVATE, 'Activate'),)
    
    name = models.CharField(max_length=64, unique=True, 
        help_text="""A unique name for this slice matching the regular expression
            ^[a-z][_0-9a-z]*[0-9a-z]$.""", 
        validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'), 
            'Enter a valid name.', 'invalid')])
    uuid = fields.UUIDField(auto=True, unique=True)
    pubkey = models.TextField(null=True, blank=True, help_text="""A PEM-encoded 
        RSA public key for this slice (used by SFA).""")
    description = models.TextField(blank=True, help_text="""An optional free-form
        textual description of this slice.""")
    expires_on = models.DateField(null=True, blank=True, default=get_expires_on,
        help_text="""Expiration date of this slice. Automatically deleted once 
        expires.""")
    instance_sn = models.PositiveIntegerField(default=0, blank=True, 
        help_text="""The number of times this slice has been instructed to be 
        reset (instance sequence number).""")
    new_sliver_instance_sn = models.PositiveIntegerField(default=0, blank=True, 
        help_text="""Instance sequence number for newly created slivers.""")
    # TODO: implement what vlan_nr.help_text says.
    vlan_nr = models.IntegerField(null=True, blank=True, help_text="""A VLAN number 
        allocated to this slice. The only values that can be set are null which 
        means that no VLAN is wanted for the slice, and -1 which asks the server 
        to allocate for the slice a new VLAN number (2 <= vlan_nr < 0xFFF) 
        while the slice is instantiated (or active). It cannot be changed on an 
        instantiated slice with slivers having isolated interfaces.""")
    exp_data = models.FileField(blank=True, upload_to=settings.SLICE_EXP_DATA_DIR,
        help_text=""".tar.gz archive containing experiment data for slivers (if
            they do not explicitly indicate one)""", 
        validators=[validators.RegexValidator(re.compile('.*\.tar\.gz'), 
            'Upload a valid .tar.gz file', 'invalid')])
    set_state = models.CharField(max_length=16, choices=STATES, default=REGISTER)
    template = models.ForeignKey(Template, help_text="""The template to be used 
        by the slivers of this slice (if they do not explicitly indicate one).""")
    users = models.ManyToManyField(User, help_text="""A ist of users able to 
        login as root in slivers using their authentication tokens (usually an 
        SSH key).""")
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # FIXME prevent modifications on vlan_nr once is seted
        if self.vlan_nr == -1:
            if self.set_state == self.INSTANTIATE:
                self.vlan_nr = self._get_vlan_nr()
            elif not self.set_state == self.REGISTER:
                raise self.VlanAllocationError('You Cannot set this vlan')
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
            raise self.VlanAllocationError("No vlan address space left")
        return last_nr + 1
    
    class VlanAllocationError(Exception): pass
    
    def force_update(self, async=False):
        if async: defer(force_slice_update.delay, self.pk)
        else: force_slice_update(self.pk)


class SliceProp(models.Model):
    slice = models.ForeignKey(Slice)
    name = models.CharField(max_length=64)
    value = models.CharField(max_length=256)
    
    class Meta:
        unique_together = ('slice', 'name')
    
    def __unicode__(self):
        return self.name


class Sliver(models.Model):
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey(Node)
    description = models.CharField(max_length=256, blank=True, help_text="""An
        optional free-form textual description of this sliver.""")
    instance_sn = models.PositiveIntegerField(default=0, blank=True,
        help_text="""The number of times this sliver has been instructed to be 
        reset (instance sequence number).""")
    exp_data = models.FileField(blank=True, upload_to=settings.SLICE_EXP_DATA_DIR,
        help_text=".tar.gz archive containing experiment data for this sliver.", 
        validators=[validators.RegexValidator(re.compile('.*\.tar\.gz'), 
            'Upload a valid .tar.gz file', 'invalid')])
    template = models.ForeignKey(Template, null=True, blank=True, help_text="""
        If present, the template to be used by this sliver, instead of the one
        specified by the slice.""")
    
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
    sliver = models.ForeignKey(Sliver)
    name = models.CharField(max_length=64)
    value = models.CharField(max_length=256)
    
    class Meta:
        unique_together = ('sliver', 'name')
    
    def __unicode__(self):
        return self.name


class SliverIface(models.Model):
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
    sliver = models.ForeignKey(Sliver)
    parent = models.ForeignKey('nodes.DirectIface', unique=True)
    
    class Meta:
        unique_together = ['sliver', 'parent']
    
    @property
    def use_default_gw(self):
        return None


class IpSliverIface(SliverIface):
    use_default_gw = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class PublicIface(IpSliverIface):
    sliver = models.ForeignKey(Sliver)


class PrivateIface(IpSliverIface):
    sliver = models.OneToOneField(Sliver)



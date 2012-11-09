import string
#from common.utils import less_significant_bits, more_significant_bits
from datetime import datetime
from django_extensions.db import fields
from django_transaction_signals import defer
from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from hashlib import sha256
from nodes.models import Node
from nodes import settings as node_settings
from slices import settings
from slices.tasks import force_slice_update, force_sliver_update
import re

# TODO protect exp_data and data files (like in firmware.build.image)

def get_expires_on():
    return datetime.now() + settings.SLICE_EXPIRATION_INTERVAL


class Template(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=32, choices=settings.TEMPLATE_TYPES,
        default=settings.DEFAULT_TEMPLATE_TYPE)
    arch = models.CharField(verbose_name="Architecture", max_length=32, 
        choices=settings.TEMPLATE_ARCHS, default=settings.DEFAULT_TEMPLATE_ARCH)
    is_active = models.BooleanField(default=True)
    data = models.FileField(upload_to=settings.TEMPLATE_DATA_DIR)
    
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
        help_text="""An optional, unique name for this slice matching the regular
            expression ^[a-z][_0-9a-z]*[0-9a-z]$.""", 
        validators=[validators.RegexValidator(re.compile('^[\w.@+-]+$'), 
            'Enter a valid name.', 'invalid')])
    uuid = fields.UUIDField(auto=True, unique=True)
    pubkey = models.TextField(null=True, blank=True, help_text="""A PEM-encoded 
        RSA public key for this slice (used by SFA).""")
    description = models.TextField(blank=True)
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
    exp_data = models.FileField(help_text="Experiment Data", blank=True,
        upload_to=settings.SLICE_EXP_DATA_DIR)
    set_state = models.CharField(max_length=16, choices=STATES, default=REGISTER)
    template = models.ForeignKey(Template)
    users = models.ManyToManyField(User, help_text="""A ist of users able to login
        as root in slivers using their authentication tokens (usually an SSH key).""")
    
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
    description = models.CharField(max_length=256, blank=True)
    instance_sn = models.PositiveIntegerField(default=0, blank=True,
        help_text="""The number of times this sliver has been instructed to be 
        reset (instance sequence number).""")
    exp_data = models.FileField(help_text="Experiment Data", blank=True,
        upload_to=settings.SLICE_EXP_DATA_DIR)
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

    #<mac-prefix-msb>:<mac-prefix-lsb>:<node-id-msb>:<node-id-lsb>:<sliver-n>:<interface-n>
    # example 06:ab:04:d2:05:00
    # operations works properly (FIXME: check if access to info works!)
    @property
    def mac_addr(self):
        node = self.parent.node

        words = [
            more_significant_bits(node.sliver_mac_prefix),
            less_significant_bits(node.sliver_mac_prefix),
            more_significant_bits(node.id),
            less_significant_bits(node.id),
            number_to_hex_str(self.sliver.nr, 2),
            number_to_hex_str(self.nr, 2)
        ]
        
        return string.join(words, ':')

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

    # https://wiki.confine-project.eu/arch:addressing
    @property
    def ipv6_addr(self): #Testbed management IPv6 network (local bridge)
    #<node.mgmt_ipv6_prefix>:<Node.id in HEX>:10<Iface.nr in HEX>:<Slice.id in HEX>
        ipv6_prefix = node_settings.MGMT_IPV6_PREFIX.split(':')
        ipv6_words = ipv6_prefix[:3]
        ipv6_words.extend([
            number_to_hex_str(self.sliver.node.id, 4), # Node.id
            '10' + number_to_hex_str(self.nr, 2), # Iface.nr
            number_to_hex_str(self.sliver.slice.id, 4) # Slice.id
        ])
        return string.join(ipv6_words, ':')

    @property
    def ipv4_addr(self):
        return 'TODO'


class PrivateIface(IpSliverIface):
    sliver = models.OneToOneField(Sliver)

    # https://wiki.confine-project.eu/arch:addressing
    @property
    def ipv6_addr(self):
        # <priv_ipv6_prefix>:0:1000:<Slice.id in HEX>
        priv_ipv6_prefix = node_settings.PRIV_IPV6_PREFIX.split(':')

        ip_words = priv_ipv6_prefix[:3] #'fd5f:eee5:a6ad::/48'
        ip_words.extend(['0:1000', int_to_ipv6(self.sliver.slice.id)])
        return string.join(ip_words, ':')

    @property
    def ipv4_addr(self):

        ## X.Y.Z.S is the address of sliver #S during its lifetime (called the sliver's private IPv4 address).
        # X.Y.Z == prefix
        # S = sliver #nubmber
        self.sliver.node.priv_ipv4_prefix
        self.sliver.nr #u8
        # build ip in string mode
        return 'TODO'


def less_significant_bits(u16):
    return '%.2x' % (u16 & 0xff)

def more_significant_bits(u16):
    return '%.2x' % (u16 >> 8)

def number_to_hex_str(number, digits):
    assert digits <= 8, "Precision %d too large? (max 8)" % digits
    return ('%.' + str(digits) + 'x') % number

def int_to_ipv6(number):
    words = [
        number_to_hex_str(number >> 32, 4),
        number_to_hex_str((number >> 16) & 0xffff, 4),
        number_to_hex_str(number & 0xffff, 4)
        ]
    return string.join(words, ':')

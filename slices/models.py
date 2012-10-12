from django_extensions.db import fields
from django.contrib.auth.models import User
from django.db import models
from slices import settings


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


class Slice(models.Model):
    REGISTER = 'register'
    INSTANTIATE = 'instantiate'
    ACTIVATE = 'activate'
    STATES = ((REGISTER, 'Register'),
              (INSTANTIATE, 'Instantiate'),
              (ACTIVATE, 'Activate'),)

    name = models.CharField(max_length=64)
    uuid = fields.UUIDField(auto=True, unique=True)
    pubkey = models.TextField(null=True, blank=True, help_text="""A PEM-encoded 
        RSA public key for this slice (used by SFA).""")
    description = models.TextField(blank=True)
    expires_on = models.DateField(null=True, blank=True, help_text="""Expiration 
        date of this slice. Automatically deleted once expires.""")
    instance_sn = models.PositiveIntegerField(default=0, blank=True, 
        help_text="""The number of times this slice has been instructed to be 
        reset (instance sequence number).""")
    # TODO this looks like a dynamic attribute to me
    new_sliver_instance_sn = models.PositiveIntegerField(default=0, blank=True, 
        help_text="""Instance sequence number that newly created slivers will get.""")
    vlan_nr = models.IntegerField(null=True, blank=True, help_text="""A VLAN 
        number allocated to this slice by the server. The only values that can 
        be /set/ are null (no VLAN wanted) and -1 (asks the server to allocate a 
        new VLAN number (2 <= vlan_nr < 0xFFF) on slice instantiation).""")
    exp_data = models.FileField(help_text="Experiment Data",
        upload_to=settings.SLICE_EXP_DATA_DIR)
    set_state = models.CharField(max_length=16, choices=STATES, default=REGISTER)
    template = models.ForeignKey(Template)
    users = models.ManyToManyField(User, help_text="""A ist of users able to login
        as root in slivers using their authentication tokens (usually an SSH key).""")

    def __unicode__(self):
        return self.name


class SliceProp(models.Model):
    slice = models.ForeignKey(Slice)
    name = models.CharField(max_length=64, unique=True)
    value = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.name


class Sliver(models.Model):
    description = models.CharField(max_length=256)
    instance_sn = models.PositiveIntegerField(default=0, blank=True, 
        help_text="""The number of times this sliver has been instructed to be 
        reset (instance sequence number).""")
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey('nodes.Node')
    
    def __unicode__(self):
        return self.description


class SliverProp(models.Model):
    sliver = models.ForeignKey(Sliver)
    name = models.CharField(max_length=64, unique=True)
    value = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.name


class SliverIface(models.Model):
    name = models.CharField(max_length=16)

    class Meta:
        abstract = True

    def __unicode__(self):
        return str(self.pk)


class IsolatedIface(SliverIface):
    sliver = models.ForeignKey(Sliver)
    parent = models.ForeignKey('nodes.RdDirectIface', null=True, blank=True)

    class Meta:
        unique_together = ['sliver', 'parent']


class IpSliverIface(SliverIface):
    use_default_gw = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class PublicIface(IpSliverIface):
    sliver = models.ForeignKey(Sliver)


class PrivateIface(IpSliverIface):
    sliver = models.OneToOneField(Sliver)



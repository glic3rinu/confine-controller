from datetime import datetime
from django_extensions.db import fields
from django.contrib.auth.models import User
from django.db import models
from nodes.models import Node
from slices import settings


class Template(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=32, choices=settings.TEMPLATE_TYPES,
        default=settings.DEFAULT_TEMPLATE_TYPE)
    arch = models.CharField(verbose_name="Architecture", max_length=32, 
        choices=settings.TEMPLATE_ARCHS, default=settings.DEFAULT_TEMPLATE_ARCH)
    is_active = models.BooleanField(default=True)
    data = models.FileField(upload_to=settings.TEMPLATE_DATA_DIR, blank=True)
    
    def __unicode__(self):
        return self.name


def get_expires_on():
    return datetime.now() + settings.SLICE_EXPIRATION_INTERVAL


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
    expires_on = models.DateField(null=True, blank=True, default=get_expires_on,
        help_text="""Expiration date of this slice. Automatically deleted once expires.""")
    instance_sn = models.PositiveIntegerField(default=0, blank=True, 
        help_text="""The number of times this slice has been instructed to be 
        reset (instance sequence number).""")
    new_sliver_instance_sn = models.PositiveIntegerField(default=0, blank=True, 
        help_text="""Instance sequence number that newly created slivers will get.""")
    vlan_nr = models.IntegerField(null=True, blank=True, help_text="""A VLAN 
        number allocated to this slice by the server. The only values that can 
        be /set/ are null (no VLAN wanted) and -1 (asks the server to allocate a 
        new VLAN number (2 <= vlan_nr < 0xFFF) on slice instantiation).""")
    exp_data = models.FileField(help_text="Experiment Data", blank=True,
        upload_to=settings.SLICE_EXP_DATA_DIR)
    set_state = models.CharField(max_length=16, choices=STATES, default=REGISTER)
    template = models.ForeignKey(Template)
    users = models.ManyToManyField(User, help_text="""A ist of users able to login
        as root in slivers using their authentication tokens (usually an SSH key).""")
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.vlan_nr == -1 and self.set_state == self.INSTANTIATE:
            self.vlan_nr = self._get_vlan_nr()
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
    def num_slivers(self):
        return self.sliver_set.all().count()
    
    def renew(self):
        self.expires_on = datetime.now() + settings.SLICE_EXPIRATION_INTERVAL
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


class SliceProp(models.Model):
    slice = models.ForeignKey(Slice)
    name = models.CharField(max_length=64, unique=True)
    value = models.CharField(max_length=256)
    
    class Meta:
        unique_together = ('slice', 'name')
    
    def __unicode__(self):
        return self.name


class Sliver(models.Model):
    description = models.CharField(max_length=256, blank=True)
    instance_sn = models.PositiveIntegerField(default=0, blank=True,
        help_text="""The number of times this sliver has been instructed to be 
        reset (instance sequence number).""")
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey(Node)
    
    def __unicode__(self):
        return self.description if self.description else str(self.id)
    
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


@property
def num_slivers(self):
    return self.sliver_set.all().count()
Node.num_slivers = num_slivers


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
    parent = models.ForeignKey('nodes.DirectIface', null=True, blank=True)
    
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



from common import fields
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
import settings


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
    INSTANTIATE = 'instantiate'
    ACTIVATE = 'activate'
    STATES = ((INSTANTIATE, _('Instantiate')),
              (ACTIVATE, _('Activate')),)

    uuid = fields.UUIDField(auto=True)
    name = models.CharField(max_length=64)
    pubkey = models.TextField("Public Key")
    description = models.TextField(blank=True)
    expires_on = models.DateField(null=True, blank=True)
    instance_sn = models.IntegerField(verbose_name="Instance Sequence Number")
    vlan_nr = models.IntegerField("Vlan Number")
    exp_data = models.FileField(verbose_name="Experiment Data",
        upload_to=settings.SLICE_EXP_DATA_DIR)
    set_state = models.CharField(max_length=16, choices=STATES, default=INSTANTIATE)
    template = models.ForeignKey(Template)
    users = models.ManyToManyField(User)

    def __unicode__(self):
        return str(self.uuid)

class SliceProp(models.Model):
    slice = models.ForeignKey(Slice)
    name = models.CharField(max_length=64)
    value = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.name


class Sliver(models.Model):
    description = models.CharField(max_length=256)
    instance_sn = models.IntegerField(verbose_name="Instance Sequence Number")
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey('nodes.Node')
    
    def __unicode__(self):
        return self.description


class SliverProp(models.Model):
    sliver = models.ForeignKey(Sliver)
    name = models.CharField(max_length=64)
    value = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.name


class SliverIface(models.Model):
    name = models.CharField(max_length=16, default='eth')

    class Meta:
        abstract = True

    def __unicode__(self):
        return str(self.pk)


class IsolatedIface(SliverIface):
    sliver = models.ForeignKey(Sliver)
    parent_name = models.CharField(max_length=16, default='eth')


class IpSliverIface(SliverIface):
    use_default_gw = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class PublicIface(IpSliverIface):
    sliver = models.ForeignKey(Sliver)


class PrivateIface(IpSliverIface):
    sliver = models.OneToOneField(Sliver)


from datetime import datetime
from hashlib import sha256

from django_transaction_signals import defer
from django.conf import settings as project_settings
from django.contrib.auth import get_user_model
from django.core import validators
from django.core.files.storage import FileSystemStorage
from django.db import models
from IPy import IP
from private_files import PrivateFileField

from common.fields import MultiSelectField
from common.ip import lsb, msb, int_to_hex_str, split_len
from common.validators import validate_net_iface_name, validate_prop_name
from nodes.models import Node
from nodes import settings as node_settings

from . import settings
from .tasks import force_slice_update, force_sliver_update


private_storage = FileSystemStorage(location=project_settings.PRIVATE_MEDIA_ROOT)


def get_expires_on():
    """ Used by slice.renew and Slice.expires_on """
    return datetime.now() + settings.SLICE_EXPIRATION_INTERVAL


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
    type = models.CharField(max_length=32, choices=settings.TEMPLATE_TYPES,
        help_text='The system type of this template. Roughly equivalent to the '
                  'distribution the template is based on, e.g. debian (Debian, '
                  'Ubuntu...), fedora (Fedora, RHEL...), suse (openSUSE, SUSE '
                  'Linux Enterprise...). To instantiate a sliver based on a '
                  'template, the research device must support its type.',
        default=settings.DEFAULT_TEMPLATE_TYPE)
    node_archs = MultiSelectField(max_length=32, choices=settings.TEMPLATE_ARCHS,
        help_text='The node architectures accepted by this template (as reported '
                  'by uname -m, non-empty). Slivers using this template should '
                  'run on nodes whose architecture is listed here.')
    is_active = models.BooleanField(default=True)
    image = models.FileField(upload_to=settings.TEMPLATE_IMAGE_DIR, 
        help_text='Template\'s image file.')
    
    def __unicode__(self):
        return self.name
    
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
    exp_data = PrivateFileField(blank=True, upload_to=settings.SLICES_EXP_DATA_DIR, 
        storage=private_storage, verbose_name='Experiment Data',
        condition=lambda request, self: 
                  request.user.has_perm('slices.slice_change', obj=self),
        help_text='.tar.gz archive containing experiment data for slivers (if'
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
        if last_nr >= int('ffff', 16):
            for new_nr in range(2, int('ffff', 16)):
                if not Slice.objects.filter(vlan_nr=new_nr):
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
    description = models.CharField(max_length=256, blank=True, 
        help_text='An optional free-form textual description of this sliver.')
    instance_sn = models.PositiveIntegerField(default=0, blank=True,
        help_text='The number of times this sliver has been instructed to be '
                  'reset (instance sequence number).', 
        verbose_name='Instance Sequence Number')
    exp_data = PrivateFileField(blank=True, upload_to=settings.SLICES_EXP_DATA_DIR, 
        storage=private_storage, verbose_name='Experiment Data',
        condition=lambda request, self: 
                  request.user.has_perm('slices.sliver_change', obj=self),
        help_text='.tar.gz archive containing experiment data for this sliver.',
        validators=[validators.RegexValidator('.*\.tar\.gz', 
                   'Upload a valid .tar.gz file', 'invalid')],)
    template = models.ForeignKey(Template, null=True, blank=True, 
        help_text='If present, the template to be used by this sliver, instead '
                  'of the one specified by the slice.')
    
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
        try: 
            ifaces = [self.privateiface] 
        except PrivateIface.DoesNotExist: 
            ifaces = []
        ifaces += list(self.isolatediface_set.all())
        ifaces += list(self.mgmtiface_set.all())
        ifaces += list(self.pub6iface_set.all())
        ifaces += list(self.pub4iface_set.all())
        return ifaces
    
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


class SliverIface(models.Model):
    """
    Base class for sliver network interfaces
    """
    name = models.CharField(max_length=10,
        help_text='The name of this interface. It must match the regular '
                  'expression ^[a-z]+[0-9]*$ and have no more than 10 characters.',
        validators=[validate_net_iface_name])
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return str(self.pk)
    
    def save(self, *args, **kwargs):
        # TODO use max_pub4ifaces on pubipv4ifaces ?
        if not self.pk and len(self.sliver.interfaces) >= self.sliver.max_num_ifaces:
            raise self.IfaceAllocationError('No more space left for interfaces')
        super(SliverIface, self).save(*args, **kwargs)
    
    @property
    def type(self):
        return self._meta.verbose_name.split(' ')[0]
    
    @property
    def parent_name(self):
        if hasattr(self, 'parent'):
            return self.parent.name
        return None
    
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
            int_to_hex_str(self.nr, 2)
        ]
        return ':'.join(words)
    
    class StateNotAvailable(Exception): pass
    
    class IfaceAllocationError(Exception): pass


class ResearchIface(SliverIface):
    sliver = models.ForeignKey(Sliver)
    
    class Meta:
        abstract = True
        # FIXME: this unique constrain only takes into account The class from which
        #       inherits, a different approach is needed for ensuring unique names
        #       accross all interfaces of an sliver.
        unique_together = ['sliver', 'name']
    
    @property
    def nr(self): # 1 >= nr >= 256
        # TODO how to predict what nr is used on the node?
        return self.pk # % 256 ) + 1 ?? #FIXME


class IsolatedIface(ResearchIface):
    """
    Describes an Isolated interface of an sliver: It is used for sharing the 
    same physical interface but isolated at L3, by means of tagging all the 
    outgoing traffic with a VLAN tag per slice. By means of using an isolated 
    interface, the researcher will be able to configure it at L3, but several 
    slices may share the same physical interface.
    """
    parent = models.ForeignKey('nodes.DirectIface', unique=True)


class IpIface(ResearchIface):
    """
    Base class for IP based sliver interfaces. IP Interfaces might have assigned
    either a public or a private address.
    """
    
    class Meta:
        abstract = True


class MgmtIface(IpIface):
    """
    Describes the management network interface for an sliver.
    """
    @property
    def ipv6_addr(self): #
        """
        Testbed management IPv6 network (local bridge)
        
        Expected address calculated in the server (can be different from the
        one showed in the node, which is the real address)
        
        MGMT_IPV6_PREFIX:N:10ii:ssss:ssss:ssss/64
        """
        ipv6_words = node_settings.MGMT_IPV6_PREFIX.split(':')[:3]
        ipv6_words.extend([
            int_to_hex_str(self.sliver.node_id, 4), # Node.id
            '10' + int_to_hex_str(self.nr, 2), # Iface.nr
        ])
        # sliver id
        ipv6_words.extend(split_len(int_to_hex_str(self.sliver.slice_id, 12), 4))
        return IP(':'.join(ipv6_words))


class Pub6Iface(IpIface):
    """
    Local network interface: assigned by stateless autoconf or DHCPv6
    Describes an IPv6 Public Interface for an sliver. Traffic from a public
    interface will be bridged to the community network.
    """
    
    @property
    def ipv6_addr(self):
        raise StateNotAvailable('state address (only available from nodes)')


class Pub4Iface(IpIface):
    """
    Local network interface: assigned by DHCP or using a configuration range
    Describes an IPv4 Public Interface for an sliver. Traffic from a public
    interface will be bridged to the community network.
    """
    
    @property
    def ipv4_addr(self):
        raise StateNotAvailable('state address (only available from nodes)')


class PrivateIface(SliverIface):
    """
    Describes a Private Interface of an sliver.Traffic from a private interface 
    will be forwarded to the community network by means of NAT. Every sliver 
    will have at least a private interface.
    """
    sliver = models.OneToOneField(Sliver)
    
    class Meta:
        unique_together = ['sliver', 'name']
    
    @property
    def nr(self):
        return 0
    
    @property
    def ipv6_addr(self):
        """
        Expected address calculated in the server (can be different from the
        one showed in the node, which is the real address)
        PRIV_IPV6_PREFIX:0:1000:ssss:ssss:ssss/64
        """
        ipv6_words = node_settings.PRIV_IPV6_PREFIX.split(':')[:3]
        ipv6_words.extend(['0','1000'])
        # sliver.id
        ipv6_words.extend(split_len(int_to_hex_str(self.sliver.slice_id, 12), 4))
        return IP(':'.join(ipv6_words))
    
    @property
    def ipv4_addr(self):
        """
        X.Y.Z.S is the address of sliver #S during its lifetime (called the
        sliver's private IPv4 address).
            - X.Y.Z == prefix
            - S = sliver #number
        NOTE: this is the expected address calculated in the server (can be
        different from the one showed in the node, which is the real address)
        """
        prefix = self.sliver.node.get_priv_ipv4_prefix()
        ipv4_words = prefix.split('.')[:3]
        ipv4_words.append('%d' % self.sliver.nr)
        return IP('.'.join(ipv4_words))


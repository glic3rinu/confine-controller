from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from IPy import IP

from controller import settings as controller_settings
from controller.utils.ip import split_len, int_to_hex_str
from nodes.models import Node, Server
from pki import ca


def get_mgmt_net(self):
    """ Getter for management network generic relation """
    if not self.pk:
        # cannot get/create mgmt_net for unsaved object
        return None
    ct = ContentType.objects.get_for_model(self)
    obj, _ = MgmtNetConf.objects.get_or_create(object_id=self.pk, content_type=ct)
    return obj


class MgmtNetConf(models.Model):
    TINC = 'tinc'
    NATIVE = 'native'
    BACKENDS = (
        (TINC, 'tinc'),
        (NATIVE, 'native'),
    )
    backend = models.CharField('Backend', max_length=16,
                choices=BACKENDS, default=TINC,
                help_text='The network backend that provides access to the '
                          'management network.')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        if hasattr(self, 'content_type'):
            return u'%s_%s' % (self.content_type.model, self.object_id)
        return u'mgmtnet_%s' % self.backend
    
    @classmethod
    def reverse(cls, ip_addr):
        from .utils import reverse
        return reverse(ip_addr)
    
    @property
    def addr(self):
        """ IPV6 management address """
        ipv6_words = controller_settings.MGMT_IPV6_PREFIX.split(':')[:3]
        if self.content_type.model == 'server':
            # MGMT_IPV6_PREFIX:0:0000:rrrr:rrrr:rrrr/128
            ipv6_words.extend(['0', '0000'])
            ipv6_words.extend(split_len(int_to_hex_str(self.object_id, 12), 4))
            return IP(':'.join(ipv6_words))
        elif self.content_type.model == 'node':
            # MGMT_IPV6_PREFIX:N:0000::2/64 i
            ipv6_words.append(int_to_hex_str(self.object_id, 4))
            return IP(':'.join(ipv6_words) + '::2')
        elif self.content_type.model == 'host':
            # MGMT_IPV6_PREFIX:0:2000:hhhh:hhhh:hhhh/128
            ipv6_words.extend(['0', '2000'])
            ipv6_words.extend(split_len(int_to_hex_str(self.object_id, 12), 4))
            return IP(':'.join(ipv6_words))
    
    @property
    def address(self):
        """Alias of addr used by generic apps like pings."""
        return self.addr
    
    @property
    def is_configured(self):
        if self.backend == MgmtNetConf.TINC:
            tinc = self.content_object.tinc
            return bool(tinc and tinc.pubkey)
        else: # native
            return True
    
    def sign_cert_request(self, scr):
        """Sign a certificate request for a management network host."""
        return ca.sign_request(scr).as_pem().strip()
    
    ## backwards compatibility #157
    def tinc_client(self):
        if self.content_type.model == 'server':
            return None
        return self.tinc()

    def tinc_server(self):
        if self.content_type.model in ['node', 'host']:
            return None
        return self.tinc()

    def tinc(self):
        return getattr(self.content_object, 'tinc', None)

    def native(self):
        return None

# Monkey-Patching Section

mgmt_net = property(get_mgmt_net)

for model in [Node, Server]:
    model.add_to_class('related_mgmtnet', generic.GenericRelation('mgmtnetworks.MgmtNetConf'))
    model.add_to_class('mgmt_net', mgmt_net)

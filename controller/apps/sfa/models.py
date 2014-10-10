from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from controller.core.validators import validate_uuid, validate_rsa_pubkey
from controller.models.fields import RSAPublicKeyField
from nodes.models import Node
from slices.models import Slice
from users.models import User, Group


class SfaObject(models.Model):
    """ SFA-related data """
    uuid = models.CharField(max_length=36, unique=True,
        help_text='A universally unique identifier (UUID, RFC 4122) for this '
                  'object. Once set to a valid UUID it can not be changed.',
        validators=[validate_uuid])
    pubkey = RSAPublicKeyField('public key', unique=True,
        help_text='A unique PEM-encoded RSA public key for this object.',
        validators=[validate_rsa_pubkey])
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return unicode(self.content_object)


# Hook SfaObject support for related models
related_models = [Slice, User, Group, Node]

@property
def sfa(self):
    try: return self.related_sfaobject.get()
    except SfaObject.DoesNotExist: return None

for model in related_models:
    model.add_to_class('related_sfaobject', generic.GenericRelation('sfa.SfaObject'))
    model.add_to_class('sfa', sfa)


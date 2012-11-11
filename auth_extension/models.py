from django_extensions.db.fields import UUIDField
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from auth_extension import settings
from common.fields import MultiSelectField


class ResearchGroup(models.Model):
    name = models.CharField(max_length=256)
    
    def __unicode__(self):
        return self.name


class AuthorizedOfficial(models.Model):
    research_group = models.OneToOneField(ResearchGroup)
    name = models.CharField(max_length=128)
    surname = models.CharField(max_length=30, blank=True)
    second_surname = models.CharField(max_length=30, blank=True)
    national_id = models.CharField(max_length=16)
    address = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=20,  blank=True, 
        default=settings.DEFAULT_AUTHORIZED_OFFICIAL_CITY)
    zipcode = models.PositiveIntegerField(blank=True, null=True)
    province = models.CharField(max_length=20, blank=True, 
        default=settings.DEFAULT_AUTHORIZED_OFFICIAL_PROVINCE)
    country = models.CharField(max_length=20, 
        default=settings.DEFAULT_AUTHORIZED_OFFICIAL_COUNTRY)
    
    def __unicode__(self):
        return "%s %s %s" % (self.name, self.surname, self.second_surname)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    uuid = UUIDField(auto=True, unique=True, 
        help_text='A universally unique identifier (UUID, RFC 4122) provided for '
                  'the user on registration.')
    description = models.TextField(blank=True, 
        help_text='An optional free-form textual description of this user, it '
                  'can include URLs and other information.')
    pubkey = models.TextField('Public Key', unique=True, null=True, blank=True, 
        help_text='A PEM-encoded RSA public key for this user (used by SFA).')
    research_groups = models.ManyToManyField(ResearchGroup, blank=True)
    
    def __unicode__(self):
        return self.user.username
    
    def clean(self):
        """ Empty pubkey and cert as NULL instead of empty string """
        if self.pubkey is u'': self.pubkey = None
        super(UserProfile, self).clean()


## TODO Ensure a userprofile is created each time a new user is added 
##       at a model level (no admin).
#@receiver(post_save, sender=User, dispatch_uid="auth_extension.create_user_profile")
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        profile, created = UserProfile.objects.get_or_create(user=instance)


class TestbedPermission(models.Model):
    ACTIONS = ((1, "Create"),
               (2, "Read"),
               (3, "Update"),
               (4, "Delete"),
               (5, "Access"),)
    
    action = MultiSelectField(max_length=250, blank=True, choices=ACTIONS)
    research_group = models.ForeignKey(ResearchGroup, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    slice = models.ForeignKey('slices.Slice', null=True, blank=True)
    node = models.ForeignKey('nodes.Node', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
    
    def __unicode__(self):
        return str(self.pk)


class AuthToken(models.Model):
    """ 
    A list of authentication tokens like SSH or other kinds of public keys or 
    X.509 certificates to be used for slivers or experiments. The exact valid 
    format depends on the type of token as long as it is non-empty and only 
    contains ASCII characters. (e.g. by using PEM encoding or other ASCII armour).
    """
    user = models.ForeignKey(User)
    data = models.CharField(max_length=256)
    
    def __unicode__(self):
        return str(self.pk)


# Monkey-Patching Section

# Make UserProfile fields visible at User model as properties
for field in ['pubkey', 'uuid', 'description']:
    def getter(self, field=field):
        return getattr(self.userprofile, field)
    
    def setter(self, value, field=field):
        setattr(self.userprofile, field, value)
        self.userprofile.save()
    
    prop = property(getter, setter)
    setattr(User, field, prop)

@property
def auth_tokens(self):
    return self.authtoken_set.all().values_list('data')
User.auth_tokens = auth_tokens

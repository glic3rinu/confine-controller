from auth_extension import settings
from common.fields import MultiSelectField
from django_extensions.db.fields import UUIDField
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_syncdb
from django.dispatch import receiver


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
    city = models.CharField(max_length=20, default=settings.DEFAULT_AUTHORIZED_OFFICIAL_CITY, blank=True)
    zipcode = models.PositiveIntegerField(blank=True, null=True)
    province = models.CharField(max_length=20, default=settings.DEFAULT_AUTHORIZED_OFFICIAL_PROVINCE, blank=True)
    country = models.CharField(max_length=20, default=settings.DEFAULT_AUTHORIZED_OFFICIAL_COUNTRY)

    def __unicode__(self):
        return "%s %s %s" % (self.name, self.surname, self.second_surname)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    uuid = UUIDField(auto=True, unique=True)
    description = models.TextField(blank=True)
    pubkey = models.TextField(unique=True, blank=True, verbose_name="Public Key")
    research_groups = models.ManyToManyField(ResearchGroup, blank=True)

    def __unicode__(self):
        return self.user.username


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
    user = models.ForeignKey(User)
    data = models.CharField(max_length=256)

    def __unicode__(self):
        return str(self.pk)


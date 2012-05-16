# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

import settings
# Create your models here.

class ActivationRequest(models.Model):
    # Relations
    user = models.ForeignKey(auth_models.User,
                             verbose_name = "user")

    # Attributes
    key = models.CharField(max_length=100,
                           verbose_name = "key")

    # Functions
    def __unicode__(self):
        return "%s" % self.user.username
    class Meta:
        verbose_name = "activation request"
        verbose_name_plural = "activation requests"

class DeleteRequest(models.Model):
    # Relations
    user = models.ForeignKey(auth_models.User,
                             verbose_name = "user")

    # Attributes

    # Functions
    def __unicode__(self):
        return "%s" % self.user.username
    class Meta:
        verbose_name = "delete request"
        verbose_name_plural = "delete requests"

class ResearchGroup(models.Model):
    # Relations
    users = models.ManyToManyField(auth_models.User,
                                   verbose_name = "users",
                                   blank = True,
                                   null = True)

    # Attributes
    name = models.CharField(max_length = 150,
                            verbose_name = "name")
    

    # Functions
    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        verbose_name = "research group"
        verbose_name_plural = "research groups"

class Role(models.Model):
    # Relations
    research_group = models.ForeignKey("ResearchGroup",
                                        verbose_name = "research groups")
    users = models.ManyToManyField(auth_models.User,
                                   verbose_name = "users",
                                   related_name = "roles",
                                   blank = True,
                                   null = True)

    # Attributes
    name = models.CharField(max_length = 150,
                            verbose_name = "name")

    # Functions
    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        verbose_name = "role"
        verbose_name_plural = "roles"

class ConfinePermission(models.Model):
    # Relations
    role = models.ManyToManyField("Role",
                                  verbose_name = "role",
                                  related_name = "permissions",
                                  blank = True,
                                  null = True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    entity = generic.GenericForeignKey('content_type', 'object_id')
    
    # Attributes
    name = models.CharField(max_length = 150,
                            verbose_name = "name")
    permission = models.CharField(max_length = 10,
                                  choices = settings.PERMISSIONS,
                                  verbose_name = "permission")
    

    # Functions
    def __unicode__(self):
        return "%s" % self.name
    class Meta:
        verbose_name = "confine permission"
        verbose_name_plural = "confine permissions"

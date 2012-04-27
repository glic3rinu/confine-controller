# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth import models as auth_models

# Create your models here.

class ActivationRequest(models.Model):
    # Relations
    user = models.ForeignKey(auth_models.User)

    # Attributes
    key = models.CharField(max_length=100)

    # Functions
    def __unicode__(self):
        return "%s" % self.user.username
    class Meta:
        verbose_name = "activation request"
        verbose_name_plural = "activation requests"

class DeleteRequest(models.Model):
    # Relations
    user = models.ForeignKey(auth_models.User)

    # Attributes

    # Functions
    def __unicode__(self):
        return "%s" % self.user.username
    class Meta:
        verbose_name = "delete request"
        verbose_name_plural = "delete requests"

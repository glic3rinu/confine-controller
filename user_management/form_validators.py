# -*- coding: utf-8 -*-
from django.forms import ValidationError
from django.contrib.auth import models as auth_models

def validate_non_existing_username(value):
    user = None
    user = auth_models.User.objects.filter(username = value)
    if user:
        raise ValidationError("Username is not valid or it already exists")

def validate_non_existing_mail(value):
    user = None
    user = auth_models.User.objects.filter(email = value)
    if user:
        raise ValidationError("Mail provided is not valid or it already exists")
    
def validate_password_format(value):
    if len(value) < 6:
        raise ValidationError("Passwords must contain a minimum of 6 characters")     

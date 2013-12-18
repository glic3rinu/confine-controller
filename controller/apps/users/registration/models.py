try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.db import models

from registration.models import RegistrationManager, RegistrationProfile #as Profile

class CustomRegistrationManager(models.Manager):
    """
    Custom manager for adding extra fields (name) when registering an User
    See related info about inheritance on models Manager
    https://docs.djangoproject.com/en/1.6/topics/db/managers/#custom-managers-and-model-inheritance
    
    """
    def create_inactive_user(self, username, name, email, password,
                             site, send_email=True):
        """ Override default manager for initialize User.name """
        new_user = User.objects.create_user(username, email, password, name=name)
        new_user.is_active = False
        new_user.save()

        registration_profile = RegistrationProfile.objects.create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email(site)

        return new_user

RegistrationProfile.extra_manager = CustomRegistrationManager()

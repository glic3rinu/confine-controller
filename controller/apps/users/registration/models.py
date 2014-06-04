from django.conf import settings
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from controller.utils.options import send_email_template
from registration.models import RegistrationManager, RegistrationProfile

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


@receiver(pre_save, sender=User)
def notify_user_enabled(sender, instance, *args, **kwargs):
    """Notify by email user and operators when an account is enabled."""
    if instance.pk and instance.is_active:
        old = User.objects.get(pk=instance.pk)
        if not old.is_active:
            send_email_template('registration/account_approved.email', {},
                instance.email)
            send_email_template('registration/account_approved_operators.email',
                {'user': instance}, settings.EMAIL_REGISTRATION_APPROVE)

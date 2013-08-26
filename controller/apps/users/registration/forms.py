from django import forms
from django.utils.translation import ugettext as _
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

from captcha.fields import CaptchaField
from registration.forms import RegistrationFormUniqueEmail as RegistrationForm

class RegistrationFormUniqueEmail(RegistrationForm):
    """ 
    Since django registration v1.0 custom user class must define its ours
    form for custom models.
    See source of registration/forms.py?at=v1.0
    """
    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        else:
            return self.cleaned_data['username']

class RegistrationCaptchaForm(RegistrationFormUniqueEmail):
    """ Registration form with captcha based on django-simple-captcha """
    captcha = CaptchaField(help_text="Type the characters you see in the picture.")

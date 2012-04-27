# -*- coding: utf-8 -*-
from user_management import form_validators
from django import forms
from django.contrib.auth import models as auth_models

class RegisterForm(forms.Form):
    username = forms.CharField(required = True,
                               validators = [form_validators.validate_non_existing_username])
    password = forms.CharField(required = True,
                               widget = forms.PasswordInput,
                               validators = [form_validators.validate_password_format])
    re_password = forms.CharField(required = True,
                                  widget = forms.PasswordInput,
                                  validators = [form_validators.validate_password_format])
    email = forms.EmailField(required = True,
                             validators = [form_validators.validate_non_existing_mail])

    def clean(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get("password")
        re_password = cleaned_data.get("re_password")

        if password != re_password:
            msg = u"Provided passwords do not match"
            self._errors['password'] = self.error_class([msg])
            
            raise forms.ValidationError(msg)

        return cleaned_data

class UserForm(forms.Form):
    first_name = forms.CharField(required = True,
                               )
    last_name = forms.CharField(required = True,
                               )
    ssh_key = forms.CharField(required = True,
                                widget = forms.Textarea
                               )
class ChangePasswordForm(forms.Form):
    password = forms.CharField(required = True,
                               widget = forms.PasswordInput,
                               validators = [form_validators.validate_password_format])
    re_password = forms.CharField(required = True,
                                  widget = forms.PasswordInput,
                                  validators = [form_validators.validate_password_format])

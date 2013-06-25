from django import forms

from firmware.plugins import FirmwarePlugin


class PasswordPlugin(FirmwarePlugin):
    description = 'Enables password setting before building the image'
    
    @property
    def form(self):
        class PasswordForm(forms.Form):
            password = forms.CharField(required=False, label='password')
            password2 = forms.CharField(required=False)
        return PasswordForm
    
    def process_form_post(self, form):
        return {'password': form.cleaned_data['password']}
    
    def pre_umount(self, image, build, *args, **kwargs):
        password = kwargs.get('password', 'confine')
        # TODO finish
    pre_umount.description = 'Configuring image password'

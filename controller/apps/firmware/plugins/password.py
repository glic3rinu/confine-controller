from django import forms

from firmware.plugins import FirmwarePlugin


class PasswordPlugin(FirmwarePlugin):
    description = 'Enables password setting before building the image'
    
    def get_form(self):
        class PasswordForm(forms.Form):
            password1 = forms.CharField(label='Password', required=False,
                widget=forms.PasswordInput)
            password2 = forms.CharField(label='Password confirmation', required=False,
                widget=forms.PasswordInput)
            
            def clean_password2(self):
                password1 = self.cleaned_data.get("password1")
                password2 = self.cleaned_data.get("password2")
                if password1 and not password2:
                    raise forms.ValidationError("Both fields are required")
                if password1 and password2 and password1 != password2:
                    raise forms.ValidationError("Passwords don't match")
                return password2
        return PasswordForm
    
    def process_form_post(self, form):
        return {'password': form.cleaned_data['password2']}
    
    def pre_umount(self, image, build, *args, **kwargs):
        """ Configuring image password """
        context = {
            'pwd': kwargs.get('password', 'confine'),
            'path': image.imgae }
        run('chroot %(path)s/bin/bash -c \'echo "root:%(pwd)s"|chpasswd\'' % context)

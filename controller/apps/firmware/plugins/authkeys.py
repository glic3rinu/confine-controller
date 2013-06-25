from django import forms

from firmware.plugins import FirmwarePlugin


class AuthKeysPlugin(FirmwarePlugin):
    description = 'Enables the inclusion of user auth_tokens'
    
    @property
    def form(self):
        class AuthKeysForm(forms.Form):
            auth_keys = forms.CharField(widget=forms.Textarea(attrs={'cols': 70, 'rows': 5}))
        return AuthKeysForm
    
    def process_form_post(self, form):
        return {'auth_keys': form.cleaned_data['auth_keys']}
    
    def pre_umount(self, image, build, *args, **kwargs):
        auth_keys = kwargs.get('auth_keys', '')
        # TODO finish
    pre_umount.description = 'Configuring Auth keys file'

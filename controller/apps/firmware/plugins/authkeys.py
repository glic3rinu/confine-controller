from django import forms

from controller.core.validators import validate_ssh_pubkey
from controller.utils.system import run

from firmware.plugins import FirmwarePlugin


class AuthKeysPlugin(FirmwarePlugin):
    description = 'Enables the inclusion of user auth_tokens'
    
    def get_form(self):
        class AuthKeysForm(forms.Form):
            auth_keys = forms.CharField(required=False,
                widget=forms.Textarea(attrs={'cols': 70, 'rows': 5}))
        
            def clean_auth_keys(self):
                auth_keys = self.cleaned_data.get("auth_keys").strip()
                for ssh_pubkey in auth_keys.splitlines():
                    validate_ssh_pubkey(ssh_pubkey)
                return auth_keys
        
        return AuthKeysForm
    
    def process_form_post(self, form):
        return {'auth_keys': form.cleaned_data['auth_keys']}
    
    def pre_umount(self, image, build, *args, **kwargs):
        """ Creating ssh/authorized_keys keys file """
        auth_keys = kwargs.get('auth_keys', False)
        if auth_keys:
            context = {
                'auth_keys': auth_keys,
                'image': image.mnt }
            run('mkdir %(image)s/root/.ssh' % context)
            run('echo "%(auth_keys)s" >> %(image)s/root/.ssh/authorized_keys' % context)

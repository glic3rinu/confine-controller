from os import path

from django import forms

from controller.core.validators import validate_ssh_pubkey
from controller.utils.html import MONOSPACE_FONTS
from controller.utils.system import run

from firmware.plugins import FirmwarePlugin
from firmware.settings import FIRMWARE_PLUGINS_INITIAL_AUTH_KEYS_PATH as keys_path


class AuthKeysPlugin(FirmwarePlugin):
    verbose_name = 'SSH authorized keys'
    description = ('Enables the inclusion of user SSH Authorized Keys\n'
                   'Current authorized keys file: %s' % keys_path)
    
    def get_form(self):
        class AuthKeysForm(forms.Form):
            auth_keys = forms.CharField(required=False, help_text='Enter the SSH '
                'keys allowed to log in as root (in "authorized_keys" format). '
                'You may leave the default keys to allow centralized management '
                'of your node.',
            widget=forms.Textarea(
                attrs={'cols': 125, 'rows': 10, 'style': 'font-family:%s' % MONOSPACE_FONTS}))
            
            def __init__(self, *args, **kwargs):
                super(AuthKeysForm, self).__init__(*args, **kwargs)
                if keys_path:
                    self.fields['auth_keys'].initial = open(keys_path).read()
            
            def clean_auth_keys(self):
                auth_keys = self.cleaned_data.get("auth_keys").strip()
                for ssh_pubkey in auth_keys.splitlines():
                    if not ssh_pubkey.lstrip().startswith('#'): # ignore comments
                        validate_ssh_pubkey(ssh_pubkey)
                return auth_keys
        
        return AuthKeysForm
    
    def process_form_post(self, form):
        return {'auth_keys': form.cleaned_data['auth_keys']}
    
    def pre_umount(self, image, build, *args, **kwargs):
        """ Creating ssh authorized keys file """
        auth_keys = kwargs.get('auth_keys', '')
        context = {
            'auth_keys': auth_keys,
            'auth_keys_path': path.join(image.mnt, 'etc/dropbear/authorized_keys')
        }
        run('echo "%(auth_keys)s" > %(auth_keys_path)s' % context)
        run('chown root:root %(auth_keys_path)s' % context)
        run('chmod 0600 %(auth_keys_path)s' % context)

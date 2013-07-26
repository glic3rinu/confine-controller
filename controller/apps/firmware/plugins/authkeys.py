from django import forms

from controller.core.validators import validate_ssh_pubkey
from controller.utils.html import MONOSPACE_FONTS
from controller.utils.system import run

from firmware.plugins import FirmwarePlugin
from firmware.settings import FIRMWARE_PLUGINS_INITIAL_AUTH_KEYS_PATH


class AuthKeysPlugin(FirmwarePlugin):
    verbose_name = 'SSH authorized keys'
    description = ('Enables the inclusion of user SSH Authorized Keys\n'
                   'Current authorized keys file: %s' % FIRMWARE_PLUGINS_INITIAL_AUTH_KEYS_PATH)
    
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
                if FIRMWARE_PLUGINS_INITIAL_AUTH_KEYS_PATH:
                    self.fields['auth_keys'].initial = open(FIRMWARE_PLUGINS_INITIAL_AUTH_KEYS_PATH).read()
            
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
        """ 
        Creating ssh/authorized_keys keys file.
        WARNING: this action overrides the old keys.
        """
        auth_keys = kwargs.get('auth_keys', '')
        print "AUTH_KEYS: %s" % auth_keys
        context = {
            'auth_keys': auth_keys,
            'image': image.mnt }
        run('echo "%(auth_keys)s" > %(image)s/etc/dropbear/authorized_keys' % context)
        run('chmod 0600 %(image)s/etc/dropbear/authorized_keys' % context)


from django import forms

from controller.core.validators import validate_ssh_pubkey
from controller.utils.system import run

from firmware.plugins import FirmwarePlugin


class AuthKeysPlugin(FirmwarePlugin):
    verbose_name = 'SSH authorized keys'
    description = 'Enables the inclusion of user SSH Authorized Keys'
    
    def get_form(self):
        class AuthKeysForm(forms.Form):
            auth_keys = forms.CharField(required=False, help_text='Enter the SSH '
                'keys allowed to log in as root (in "authorized_keys" format). '
                'You may leave the default keys to allow centralized management '
                'of your node.',
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


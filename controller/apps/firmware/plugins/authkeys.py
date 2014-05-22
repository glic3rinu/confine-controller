import os

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
                'of your node. '
                'Please note that this may expose your node to an attack '
                'if the testbed registry is compromised.',
            widget=forms.Textarea(
                attrs={'cols': 125, 'rows': 10, 'style': 'font-family:%s' % MONOSPACE_FONTS}))
            
            def __init__(self, *args, **kwargs):
                super(AuthKeysForm, self).__init__(*args, **kwargs)
                # load stored authentication keys (#383)
                assert hasattr(self.node, 'keys'), "The node doesn't have keys, have you runned firmware migrations?"
                if self.node.keys.ssh_auth:
                    self.fields['auth_keys'].initial = self.node.keys.ssh_auth
                    self.fields['auth_keys'].help_text += (' <span style="color:red">'
                        'Loaded stored keys as initial value.</span>')
                elif keys_path:
                    self.fields['auth_keys'].initial = open(keys_path).read()
            
            def clean_auth_keys(self):
                auth_keys = self.cleaned_data.get("auth_keys").strip()
                for ssh_pubkey in auth_keys.splitlines():
                    if not ssh_pubkey.lstrip().startswith('#'): # ignore comments
                        validate_ssh_pubkey(ssh_pubkey)
                # store new authentication keys (#383)
                self.node.keys.ssh_auth = auth_keys
                self.node.keys.save()
                return auth_keys
        
        return AuthKeysForm
    
    def process_form_post(self, form):
        return {'auth_keys': form.cleaned_data['auth_keys']}
    
    def pre_umount(self, image, build, *args, **kwargs):
        """ Creating ssh authorized keys file """
        auth_keys = kwargs.get('auth_keys', '')
        context = {
            'auth_keys': auth_keys,
            'auth_keys_path': os.path.join(image.mnt, 'etc/dropbear/authorized_keys')
        }
        run('echo "%(auth_keys)s" > %(auth_keys_path)s' % context)
        os.chown(context['auth_keys_path'], 0, 0)
        key_stat = os.stat(context['auth_keys_path'])
        assert 0 == key_stat.st_uid == key_stat.st_gid, "Failing when changing ownership!"
        run('chmod 0600 %(auth_keys_path)s' % context)

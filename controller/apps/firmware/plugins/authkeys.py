import os

from django import forms

from controller.utils.html import MONOSPACE_FONTS
from controller.utils.system import run

from api import serializers
from firmware.models import NodeKeys
from firmware.plugins import FirmwarePlugin
from firmware.settings import FIRMWARE_PLUGINS_INITIAL_AUTH_KEYS_PATH as keys_path


def process_data(node, data):
    admins_keys = []
    if data.get('allow_node_admins'):
        for admin in node.group.admins:
            admins_keys += admin.auth_tokens.values_list('data', flat=True)
    return {
        'admins_keys': '\n'.join(admins_keys),
        'additional_keys': data['ssh_auth']
    }


class AuthKeysPlugin(FirmwarePlugin):
    verbose_name = 'SSH authorized keys'
    description = ('Enables the inclusion of user SSH Authorized Keys\n'
                   'Current authorized keys file: %s' % keys_path)
    enabled_by_default = True
    
    def get_form(self):
        class AuthKeysForm(forms.ModelForm):
            class Meta:
                model = NodeKeys
                fields = ('allow_node_admins', 'ssh_auth', 'sync_node_admins')
                widgets = {
                    'ssh_auth': forms.Textarea(attrs={'cols': 125, 'rows': 10,
                        'style': 'font-family:%s' % MONOSPACE_FONTS}),
                }
            
            def __init__(self, *args, **kwargs):
                assert hasattr(self.node, 'keys'), "The node doesn't have keys, have you runned firmware migrations?"
                # Bound nodekeys to the form (plugin forms aren't initialized)
                kwargs['instance'] = self.node.keys
                if self.node.keys.ssh_auth:
                    msg = "Loaded stored keys as initial value."
                elif keys_path:
                    kwargs['initial'] = {'ssh_auth': open(keys_path).read()}
                    msg = "Loaded default keys as initial value."
                super(AuthKeysForm, self).__init__(*args, **kwargs)
                self.fields['ssh_auth'].help_text += ' <span style="color:red">%s</span>' % msg
        
        return AuthKeysForm
    
    def get_serializer(self):
        class AuthKeysSerializer(serializers.ModelSerializer):
            class Meta:
                model = NodeKeys
                fields = ('allow_node_admins', 'ssh_auth', 'sync_node_admins')
            
            def __init__(self, node, *args, **kwargs):
                super(AuthKeysSerializer, self).__init__(*args, **kwargs)
                self.node = node
            
            def validate_ssh_auth(self, attrs, source):
                # For some reason is_valid doesn't call field validators!
                from firmware.validators import validate_ssh_auth
                validate_ssh_auth(attrs.get(source, ''))
                return attrs
            
            def process_post(self):
                assert self.is_valid()
                self.object.node = self.node
                self.save()
                return process_data(self.node, self.data)
        
        return AuthKeysSerializer
    
    def process_form_post(self, form):
        form.save() # save into db after form validation
        return process_data(form.node, form.cleaned_data)
    
    def pre_umount(self, image, build, *args, **kwargs):
        """ Creating ssh authorized keys file """
        admins_keys = kwargs.get('admins_keys', '')
        additional_keys = kwargs.get('additional_keys', '')
        auth_keys = ("# Group and node admins' keys:\n%s\n"
                     "# Additional keys:\n%s\n"
                     "# Other keys:\n" % (admins_keys, additional_keys))
        context = {
            'auth_keys': auth_keys,
            'auth_keys_path': os.path.join(image.mnt, 'etc/dropbear/authorized_keys')
        }
        run('echo "%(auth_keys)s" > %(auth_keys_path)s' % context)
        os.chown(context['auth_keys_path'], 0, 0)
        key_stat = os.stat(context['auth_keys_path'])
        assert 0 == key_stat.st_uid == key_stat.st_gid, "Failing when changing ownership!"
        run('chmod 0600 %(auth_keys_path)s' % context)

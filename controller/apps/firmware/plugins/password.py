import crypt
import random
import string
import os
from datetime import datetime

from django import forms

from controller.utils.system import run

from api import serializers
from firmware.plugins import FirmwarePlugin

def process_data(node, data):
    # Disable and reset root password
    if data['disabled']:
        node.keys.ssh_pass = None
        node.keys.save()
        return {'password': False}
    
    # Use stored password
    if node.keys.ssh_pass:
        return {'password': node.keys.ssh_pass}
    
    # Use NEW provided password - compute hash
    password = data['password']
    hash_type = 1 # 1:MD5, 2a:Blowfish, 5:SHA-256, 6:SHA-512
    salt_chars = string.ascii_letters + string.digits
    salt_length = 8 #random.randint(1, 16)
    salt = ''.join(random.choice(salt_chars) for x in range(salt_length))
    crypted_password = crypt.crypt(password, "$%i$%s$" % (hash_type, salt))
    
    # store crypted password
    node.keys.ssh_pass = crypted_password
    node.keys.save()
    return {'password': crypted_password}


class PasswordPlugin(FirmwarePlugin):
    verbose_name = 'Root password'
    description = ('Enables password setting before building the image\n'
                   'If empty the old password will be used (if any).')
    
    def get_form(self):
        class PasswordForm(forms.Form):
            disabled = forms.BooleanField(label='Disable root password authentication.',
                    required=False,
                    help_text='Disable root authentiation using password method. '
                              'Old stored password will be removed.')
            password = forms.CharField(label='Password', required=False,
                    help_text='Enter a password to be set for the root user. ',
                    widget=forms.PasswordInput)
            password2 = forms.CharField(label='Password confirmation', required=False,
                    widget=forms.PasswordInput)
            
            def __init__(self, *args, **kwargs):
                """ Show a message if the password has previously set. """
                super(PasswordForm, self).__init__(*args, **kwargs)
                assert hasattr(self.node, 'keys'), "The node doesn't have keys, have you runned firmware migrations?"
                if self.node.keys.ssh_pass:
                    self.fields['password'].help_text += ('<span style="color:red">'
                        'If empty the previous password will be used.</span>')
            
            def clean(self):
                cleaned_data = super(PasswordForm, self).clean()
                disabled = cleaned_data.get("disabled")
                new_password = cleaned_data.get("password")
                old_password = self.node.keys.ssh_pass
                if not (disabled or new_password or old_password):
                    raise forms.ValidationError("You need to provide a root "
                        "password or disable it. There is no previous one stored.")
                return cleaned_data
            
            def clean_password2(self):
                password = self.cleaned_data.get("password")
                password2 = self.cleaned_data.get("password2")
                if password and not password2:
                    raise forms.ValidationError("Both fields are required")
                if password and password2 and password != password2:
                    raise forms.ValidationError("Passwords don't match")
                return password2
        
        return PasswordForm
    
    def get_serializer(self):
        class PasswordSerializer(serializers.Serializer):
            disable_password = serializers.BooleanField(default=True)
            password = serializers.CharField(default='', required=False)
            
            def __init__(self, node, *args, **kwargs):
                super(PasswordSerializer, self).__init__(*args, **kwargs)
                self.node = node
            
            def validate(self, attrs):
                # check that password is provided or has been disabled
                if not attrs['disable_password'] and not attrs['password']:
                    raise serializers.ValidationError(
                        'You must provide a password or disable it.'
                    )
                return attrs
            
            def process_post(self):
                assert self.is_valid()
                self.data['disabled'] = self.data['disable_password']
                return process_data(self.node, self.data)
        
        return PasswordSerializer
    
    def process_form_post(self, form):
        return process_data(form.node, form.cleaned_data)
    
    def pre_umount(self, image, build, *args, **kwargs):
        """ Configuring image password """
        password = kwargs.get('password')
        
        # days since Jan 1, 1970 from now
        epoch = datetime.utcfromtimestamp(0)
        today = datetime.today()
        d = today - epoch
        
        context = {
            'image': image.mnt
        }
        # remove old uci-defaults script that generates
        run('rm -f %(image)s/etc/uci-defaults/confine-passwd.sh' % context)
        
        # generate root line for shadow file
        if password:
            line_context = {
                'pwd': password,
                'user': 'root',
                'last_changed': d.days,
                'min_days': 0,
                'max_days': 99999,
                'warn_days': 7
            }
            line = '%(user)s:%(pwd)s:%(last_changed)i:%(min_days)i:'\
                   '%(max_days)i:%(warn_days)i:::' % line_context
            context.update({
                'line': line.replace('/', '\/'),
                'shadow': os.path.join(image.mnt, 'etc/shadow'),
            })
            run("sed -i 's/^root:.*/%(line)s/' %(shadow)s" % context)

import crypt
import random
import string
import os
from datetime import datetime

from django import forms

from controller.utils.system import run

from firmware.plugins import FirmwarePlugin
from firmware.settings import FIRMWARE_PLUGINS_PASSWORD_DEFAULT as default_password


class PasswordPlugin(FirmwarePlugin):
    verbose_name = 'Root password'
    description = ('Enables password setting before building the image\n'
                   'Default password: %s' % default_password)
    
    def get_form(self):
        class PasswordForm(forms.Form):
            password1 = forms.CharField(label='Password', required=False,
                    help_text='Enter a password to be set for the root user. The '
                              'default password is %s.' % default_password,
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
        """ Calculating password hash """
        password = form.cleaned_data['password2'] or default_password
        hash_type = 6 # 1:MD5, 2a:Blowfish, 5:SHA-256, 6:SHA-512
        salt_chars = string.ascii_letters + string.digits
        salt_length = random.randint(1, 16)
        salt = ''.join(random.choice(salt_chars) for x in range(salt_length))
        crypted_password = crypt.crypt(password, "$%i$%s$" % (hash_type, salt))
        return {'password': crypted_password}
    
    def pre_umount(self, image, build, *args, **kwargs):
        """ Configuring image password """
        password = kwargs.get('password')
        
        # days since Jan 1, 1970 from now
        epoch = datetime.utcfromtimestamp(0)
        today = datetime.today()
        d = today - epoch
        
        # generate root line for shadow file
        context = {
            'pwd': password,
            'user': 'root',
            'last_changed': d.days,
            'min_days': 0,
            'max_days': 99999,
            'warn_days': 7
        }
        line = '%(user)s:%(pwd)s:%(last_changed)i:%(min_days)i:%(max_days)i:%(warn_days)i:::' % context
        
        context = {
            'line': line.replace('/', '\/'),
            'shadow': os.path.join(image.mnt, 'etc/shadow'),
            'image': image.mnt
        }
        run("sed -i 's/^root:.*/%(line)s/' %(shadow)s" % context)
        run('rm -f %(image)s/etc/uci-defaults/confine-passwd.sh' % context)

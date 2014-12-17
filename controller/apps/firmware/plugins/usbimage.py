import os

from django import forms

from controller.utils.paths import get_site_root
from controller.utils.system import run

from api import serializers
from firmware.image import Image
from firmware.plugins import FirmwarePlugin
from firmware.settings import FIRMWARE_PLUGINS_USB_IMAGE


usb_image = FIRMWARE_PLUGINS_USB_IMAGE % {'site_root': get_site_root()}


class USBImagePlugin(FirmwarePlugin):
    verbose_name = 'USB image'
    description = ('Optionally puts the firmware image into confine-install USB image.\n'
        'The base image can be downloaded from http://media.confine-project.eu/'
        'confine-install/confine-install.img.gz and stored in %s.' % usb_image)
    enabled_by_default = True
    
    def get_form(self):
        class USBImageForm(forms.Form):
            usb_image = forms.BooleanField(label='USB Image', required=False,
                help_text='Select this option if you want to install the node image '
                    'from a USB stick. This option requires a node internal hard drive.')
        return USBImageForm
    
    def get_serializer(self):
        class USBImageSerializer(serializers.Serializer):
            usb_image = serializers.BooleanField(required=False, default=False)
            
            def __init__(self, node, *args, **kwargs):
                 super(USBImageSerializer, self).__init__(*args, **kwargs)
            
            def process_post(self):
                assert self.is_valid()
                return self.data
        
        return USBImageSerializer
    
    def process_form_post(self, form):
        return {'usb_image': form.cleaned_data['usb_image']}
    
    def post_umount(self, image, build, *args, **kwargs):
        """ Creating confine-install USB image """
        if kwargs.get('usb_image', False):
            install = Image(usb_image)
            try:
                install.prepare()
                install.gunzip()
                install.mount()
                path = os.path.join(install.mnt, 'confine/*img.gz')
                dst = run('ls %s' % path).stdout
                image.gzip()
                run('mv %s %s' % (image.file, dst))
                install.umount()
            except:
                install.clean()
            image.file = install.file
            image.tmp = install.tmp
    
    def update_image_name(self, image_name, **kwargs):
        """ Updating confine-install USB image name """
        is_usb = kwargs.get('usb_image', False)
        return 'USB-'+image_name if is_usb else image_name

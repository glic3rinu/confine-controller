import os

from django import forms

from controller.utils.paths import get_site_root
from controller.utils.system import run

from firmware.image import Image
from firmware.plugins import FirmwarePlugin
from firmware.settings import FIRMWARE_PLUGINS_USB_IMAGE


class USBImagePlugin(FirmwarePlugin):
    verbose_name = 'USB image'
    description = 'Optionally puts the firmware image into confine-install USB image'
    
    def get_form(self):
        class USBImageForm(forms.Form):
            usb_image = forms.BooleanField(label='USB Image', required=False,
                help_text='Select this option if you want to flash the image into '
                    'a USB rather than flashing the image directly on the node.')
        return USBImageForm
    
    def process_form_post(self, form):
        return {'usb_image': form.cleaned_data['usb_image']}
    
    def post_umount(self, image, build, *args, **kwargs):
        """ Creating confine-install USB image """
        if kwargs.get('usb_image', False):
            try:
                context = { 'site_root': get_site_root() }
                install = Image(FIRMWARE_PLUGINS_USB_IMAGE % context)
                install.prepare()
                install.gunzip()
                install.mount()
                path = os.path.join(install.mnt, 'confine/*img.gz')
                dst = run('ls %s' % path).stdout
                run('mv %s %s' % (image.image, dst))
                install.umount()
            except:
                install.clean()
            image.clean()
            image.image = install.image
            image.tmp = install.tmp
    
    def update_image_name(self, image_name, **kwargs):
        """ Updating confine-install USB image name """
        return 'USB-'+image_name if kwargs.get('usb_image', False) else image_name

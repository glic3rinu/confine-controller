from django import forms

from controller.utils.system import run

from firmware.image import Image
from firmware.plugins import FirmwarePlugin


class USBImagePlugin(FirmwarePlugin):
    description = 'Optionally puts the firmware image into confine-install USB image'
    
    @property
    def form(self):
        class USBImageForm(forms.Form):
            usb_image = forms.BooleanField(label='USB Image', help_text='Select '
                'this option if you want to flash the image into a USB rather '
                'than flashing the image directly to your node')
        return USBImageForm
    
    def process_form_post(self, form):
        return {'usb_image': form.cleaned_data['usb_image']}
    
    def post_umount(self, image, build, *args, **kwargs):
        if kwargs.get('usb_image', False):
            install = Image('/tmp/confine-install.img.gz')
            try:
                install.prepare()
                install.gunzip()
                install.mount()
                path = os.path.join(install.mnt, 'confine/*img.gz')
                dst = run('ls %s' % path).stdout
                run('mv %s %s' % (image.image, dst))
                install.umount()
                image.umount()
                image.clean()
                image.image = install.image
            except:
                install.clean()
    post_umount.description = 'Creating confine-install USB image'
    
    # TODO hook get_dest_path 

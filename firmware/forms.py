from django import forms

from .models import Config


class GetFirmwareForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(GetFirmwareForm, self).__init__(*args, **kwargs)
        config = Config.objects.get()
        for f in config.configfile_set.filter(optional=True):
            self.fields[f.pk] = forms.BooleanField(label=f.path, required=False, 
                help_text="This file is the private key for the management overlay. "
                          "<br>Notice that the node public key will be automatically "
                          "updated and your node will lose connectivity to the "
                          "management network until the new image is not installed.</br>")


from django import forms

from firmware.models import BaseImage, Config


class OptionalFilesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(OptionalFilesForm, self).__init__(*args, **kwargs)
        config = Config.objects.get()
        for f in config.files.active().optional():
            self.fields["%s" % f.pk] = forms.BooleanField(label=f.path, required=False,
                help_text=f.help_text)


class BaseImageForm(forms.Form):
    """ Select a node base image (filtered by arch) """
    base_image = forms.ModelChoiceField(queryset=BaseImage.objects.all(), 
                    empty_label=None, widget=forms.RadioSelect,
                    help_text="Select the base image for building the firmware")
    
    def __init__(self, arch, *args, **kwargs):
        super(BaseImageForm, self).__init__(*args, **kwargs)
        qs = BaseImage.objects.filter_by_arch(arch)
        self.fields['base_image'].queryset = qs

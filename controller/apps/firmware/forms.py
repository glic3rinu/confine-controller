from django import forms
from django.utils.safestring import mark_safe

from nodes.models import ServerApi

from .models import BaseImage, Config


class OptionalFilesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(OptionalFilesForm, self).__init__(*args, **kwargs)
        config = Config.objects.get()
        for f in config.files.active().optional():
            self.fields["%s" % f.pk] = forms.BooleanField(label=f.path, required=False,
                help_text=f.help_text, initial=True)


class HackedRadioSelect(forms.RadioSelect.renderer):
    """ here be dragons """
    def render(self):
        options = u'<br>'.join([u'%s' % w for w in self])
        return mark_safe('<ul style="margin: 2px; padding: 2px;">%s</ul>' % options)


class BaseImageForm(forms.Form):
    """ Select a node base image (filtered by arch) """
    base_image = forms.ModelChoiceField(queryset=BaseImage.objects.all(),
                    empty_label=None, widget=forms.RadioSelect(renderer=HackedRadioSelect),
                    help_text="Choose a base image flavour for building the firmware")
    
    def __init__(self, arch, *args, **kwargs):
        super(BaseImageForm, self).__init__(*args, **kwargs)
        qs = BaseImage.objects.filter_by_arch(arch).order_by('-default')
        self.fields['base_image'].queryset = qs
        self.fields['base_image'].initial = qs[0] if qs.exists() else None


class RegistryApiModelChoiceField(forms.ModelChoiceField):
    def __init__(self, **kwargs):
        qs = ServerApi.objects.filter(type=ServerApi.REGISTRY)
        super(RegistryApiModelChoiceField, self).__init__(queryset=qs, **kwargs)

    def label_from_instance(self, obj):
        island_name = obj.island.name if obj.island else 'Management network'
        return "%s (%s @ %s)" % (obj.base_uri, obj.server.name, island_name)


class RegistryApiForm(forms.ModelForm):
    registry_api = RegistryApiModelChoiceField(required=False,
                        label="Registry API service",
                        help_text="Existing registry API services that can be chosen "
                                  "to fill URI and certificate automatically.")
    
    class Meta:
        model = ServerApi
        fields = ['registry_api', 'base_uri', 'cert']
        widgets = {
            'base_uri': forms.URLInput(attrs={'class': 'vURLField'}),
            'cert': forms.Textarea(attrs={'class': 'vLargeTextField'})
        }
        help_texts = {
            'base_uri': 'A URI where an endpoint of the registry API can be accessed.',
            'cert': ('An X.509 PEM-encoded certificate for the API endpoint. '
                     'Required for HTTPS and other encrypted connections.')
        }
    
    def clean(self):
        cleaned_data = super(RegistryApiForm, self).clean()
        base_uri = cleaned_data.get("base_uri")
        cert = cleaned_data.get("cert")
        if base_uri and base_uri.startswith('https://') and not cert:
            raise forms.ValidationError("Certificate is required for HTTPS.")
        return cleaned_data
    
    def validate_unique(self):
        """
        Disable unique validation because no object will be created.
        """
        pass

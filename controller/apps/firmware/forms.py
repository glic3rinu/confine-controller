from django import forms
from django.utils.safestring import mark_safe

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

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import Config


class BaseImageFormSet(BaseInlineFormSet):
    def clean(self):
        """ Prevents repeated architectures """
        current_archs = []
        for form in self.forms:
            archs = form.cleaned_data['architectures']
            for arch in archs:
                if arch in current_archs:
                    raise ValidationError("Architecture '%s' selected twice or more times." % arch)
            current_archs += archs
        super(BaseImageFormSet, self).clean()


class OptionalFilesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(OptionalFilesForm, self).__init__(*args, **kwargs)
        config = Config.objects.get()
        for f in config.files.active().optional():
            self.fields["%s" % f.pk] = forms.BooleanField(label=f.path, required=False,
                help_text=f.help_text)

from django import forms

from .models import Config


class OptionalFilesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(OptionalFilesForm, self).__init__(*args, **kwargs)
        config = Config.objects.get()
        for f in config.configfile_set.active().optional():
            self.fields["%s" % f.pk] = forms.BooleanField(label=f.path, required=False,
                help_text=f.help_text)

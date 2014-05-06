from django import forms
from django.utils.safestring import mark_safe

from controller.utils.html import MONOSPACE_FONTS

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


class NodeKeysForm(forms.Form):
    """
    Provide a form to retrieve or provide node private keys
    allowing keeping them between firmware generations.
    """
    cert = forms.CharField(label='API certificate private key', required=False,
        widget=forms.Textarea(attrs={
            'cols': 70, 'rows': 10,
            'style': 'font-family:%s' % MONOSPACE_FONTS
        }))
    private = forms.CharField(label='API node private key', required=False,
        widget=forms.Textarea(attrs={
            'cols': 70, 'rows': 10,
            'style': 'font-family:%s' % MONOSPACE_FONTS
        }))
    tinc = forms.CharField(label='tinc private key', required=False,
        widget=forms.Textarea(attrs={
            'cols': 70, 'rows': 10,
            'style': 'font-family:%s' % MONOSPACE_FONTS
        }))

    def __init__(self, *args, **kwargs):
        self.node = kwargs.pop('node', None)
        readonly = kwargs.pop('readonly', False)
        super(NodeKeysForm, self).__init__(*args, **kwargs)
        assert hasattr(self.node, 'keys'), "The node doesn't have keys, have you runned firmware migrations?"
        for field_name in ['cert', 'private', 'tinc']:
            self.fields[field_name].initial = getattr(self.node.keys, field_name)
            if readonly:
                self.fields[field_name].widget.attrs['readonly'] = True
                self.fields[field_name].widget.attrs['disabled'] = True

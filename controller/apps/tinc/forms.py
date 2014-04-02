from django import forms
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet
from django.core.exceptions import ValidationError

from .models import TincHost

class TincHostInlineFormSet(BaseGenericInlineFormSet):
    def clean(self):
        cleaned_data = super(TincHostInlineFormSet, self).clean()
        
        is_blank = len(self.forms) == 0 or self.forms[0].cleaned_data == {}
        
        # Check if tinc configuration is provided if necessary
        # but allow create an instance missconfigured
        # FIXME: doesn't work if mgmt_net.backend changed from 'native' to 'tinc'
        # because hasn't be saved yet
        if (self.instance.pk and
            self.instance.mgmt_net.backend == 'tinc' and
            is_blank):
            raise ValidationError("Please provide tinc backend configuration. "
                                  "Required because 'tinc' is choosed as "
                                  "management network backend.")
        return cleaned_data

class TincHostInlineForm(forms.ModelForm):
    class Meta:
        model = TincHost
    
    def save(self, commit=True):
        if self.cleaned_data['clear_pubkey']:
            self.instance.pubkey = None
        super(TincHostInlineForm, self).save(commit=commit)

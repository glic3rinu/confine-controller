from django import forms

from .models import TincHost


class TincHostInlineForm(forms.ModelForm):
    clear_pubkey = forms.BooleanField(label='Clear pubkey', required=False,
        help_text="Select if you want to delete the current public key for adding "
                  "a new one")
    
    class Meta:
        model = TincHost
    
    def save(self, commit=True):
        if self.cleaned_data['clear_pubkey']:
            self.instance.pubkey = None
        super(TincHostInlineForm, self).save(commit=commit)

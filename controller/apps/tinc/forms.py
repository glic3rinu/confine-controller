from django import forms
from django.core.exceptions import ValidationError

from controller.forms.models import GroupedModelChoiceField

from .models import TincHost


def get_gateway_label(content_type):
    label = {
        'host': "Hosts (run by users)",
        'node': "Nodes (run by groups)",
        'server': "Servers (run by operators)",
    }
    return label[content_type.model]

class TincHostInlineForm(forms.ModelForm):
    clear_pubkey = forms.BooleanField(label='Clear pubkey', required=False,
        help_text="Select if you want to delete the current public key for "
                  "adding a new one.")
    default_connect_to = GroupedModelChoiceField(label='Default connect to',
        group_by_field='content_type', group_label=get_gateway_label,
        queryset=TincHost.objects.servers(),
        required=False)
    
    class Meta:
        model = TincHost
        fields = ('pubkey',)
    
    def clean_default_connect_to(self):
        default_connect_to = self.cleaned_data['default_connect_to']
        if (default_connect_to is None and self.instance and
            self.instance.content_type.model in ['node', 'host']):
            raise ValidationError('You should configure a default gateway.')
        return default_connect_to
    
    def save(self, commit=True):
        if self.cleaned_data['clear_pubkey']:
            self.instance.pubkey = None
        super(TincHostInlineForm, self).save(commit=commit)

from django import forms

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
        queryset=TincHost.objects.filter(addresses__isnull=False))
    
    class Meta:
        model = TincHost
    
    def save(self, commit=True):
        if self.cleaned_data['clear_pubkey']:
            self.instance.pubkey = None
        super(TincHostInlineForm, self).save(commit=commit)

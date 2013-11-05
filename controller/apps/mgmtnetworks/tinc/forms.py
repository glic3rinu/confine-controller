from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from controller.forms.widgets import ShowText

from .models import TincClient, TincServer


class TincHostInlineForm(forms.ModelForm):
    clear_pubkey = forms.BooleanField(label='Clear pubkey', required=False,
        help_text="Select if you want to delete the current public key for adding "
                  "a new one")
    
    def save(self, commit=True):
        if self.cleaned_data['clear_pubkey']:
            self.instance.pubkey = None
        super(TincHostInlineForm, self).save(commit=commit)


class TincClientInlineForm(TincHostInlineForm):
    class Meta:
        model = TincClient


class TincServerInlineForm(TincHostInlineForm):
    class Meta:
        model = TincServer


class HostInlineAdminForm(forms.ModelForm):
    host = forms.CharField(label="Host", widget=ShowText(bold=True))
    pk = forms.CharField(label="ID", widget=ShowText(bold=True))
    tinc_name = forms.CharField(label="Tinc Name", widget=ShowText())
    
    class Meta:
        fields = []
    
    def __init__(self, *args, **kwargs):
        super(HostInlineAdminForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            host_change = reverse('admin:tinc_host_change', args=(instance.pk,))
            self.initial['host'] = mark_safe("""<a href='%s' id='add_id_user' 
                onclick='return showAddAnotherPopup(this);'>%s </a>""" % (host_change, instance))
            self.initial['pk'] = instance.pk
            self.initial['tinc_name'] = instance.tinc.name

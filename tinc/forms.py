from common.widgets import ShowText
from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


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

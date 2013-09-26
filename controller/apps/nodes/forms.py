from django import forms
from django.core.urlresolvers import reverse
from django.forms.models import BaseInlineFormSet
from django.utils.safestring import mark_safe

from controller.forms.widgets import ShowText

from .settings import NODES_NODE_DIRECT_IFACES_DFLT
from .validators import validate_csr


class NodeInlineAdminForm(forms.ModelForm):
    node = forms.CharField(label="Node", widget=ShowText(bold=True))
    pk = forms.CharField(label="ID", widget=ShowText(bold=True))
    arch = forms.CharField(label="Arch", widget=ShowText())
    set_state = forms.CharField(label="Set State", widget=ShowText(bold=True))
    
    class Meta:
        fields = []
    
    def __init__(self, *args, **kwargs):
        super(NodeInlineAdminForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            node_change = reverse('admin:nodes_node_change', args=(instance.pk,))
            self.initial['node'] = mark_safe("""<a href='%s' id='add_id_user'
                onclick='return showAddAnotherPopup(this);'>%s </a>""" % (node_change, instance))
            self.initial['pk'] = instance.pk
            self.initial['arch'] = instance.arch
            self.initial['set_state'] = instance.set_state


class RequestCertificateForm(forms.Form):
    csr = forms.CharField(widget=forms.Textarea(attrs={'cols': '70', 'rows': '20'}))
    
    def clean_csr(self):
        csr = self.cleaned_data['csr']
        validate_csr(csr, self.node)
        return csr.strip()


class DirectIfaceInlineFormSet(BaseInlineFormSet):
    """ Provides initial Direct ifaces """
    def __init__(self, *args, **kwargs):
        if not kwargs['instance'].pk and 'data' not in kwargs:
            total = len(NODES_NODE_DIRECT_IFACES_DFLT)
            initial_data = {
                'direct_ifaces-TOTAL_FORMS': unicode(total),
                'direct_ifaces-INITIAL_FORMS': u'0',
                'direct_ifaces-MAX_NUM_FORMS': u'',}
            for num, name in enumerate(NODES_NODE_DIRECT_IFACES_DFLT):
                initial_data['direct_ifaces-%d-name' % num] = name
            kwargs['data'] = initial_data
        super(DirectIfaceInlineFormSet, self).__init__(*args, **kwargs)

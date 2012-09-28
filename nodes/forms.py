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
            host_change = reverse('admin:nodes_host_change', args=(instance.pk,))
            self.initial['host'] = mark_safe("""<a href='%s' id='add_id_user' 
                onclick='return showAddAnotherPopup(this);'>%s </a>""" % (host_change, instance))
            self.initial['pk'] = instance.pk
            self.initial['tinc_name'] = instance.tinc_name


class NodeInlineAdminForm(forms.ModelForm):
    """ 
    Read-only form for displaying slivers in slice admin change form.
    Also it provides popup links to each Node admin change form.
    """
    node = forms.CharField(label="Node", widget=ShowText(bold=True))
    pk = forms.CharField(label="ID", widget=ShowText(bold=True))
    cn_url = forms.CharField(label="Node CN URL", widget=ShowText(bold=True))
    rd_arch = forms.CharField(label="RD Arch", widget=ShowText())
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
            self.initial['cn_url'] = mark_safe("<a href='%s'>%s</a>" % (instance.cn_url, 
                instance.cn_url))
            self.initial['rd_arch'] = instance.researchdevice.arch
            self.initial['set_state'] = instance.set_state


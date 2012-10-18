from common.widgets import ShowText
from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


class NodeInlineAdminForm(forms.ModelForm):
    node = forms.CharField(label="Node", widget=ShowText(bold=True))
    pk = forms.CharField(label="ID", widget=ShowText(bold=True))
    cn_url = forms.CharField(label="Node CN URL", widget=ShowText(bold=True))
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
            self.initial['cn_url'] = mark_safe("<a href='%s'>%s</a>" % (instance.cn_url, 
                instance.cn_url))
            self.initial['arch'] = instance.arch
            self.initial['set_state'] = instance.set_state


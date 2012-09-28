from common.widgets import ShowText
from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

class SliverInlineAdminForm(forms.ModelForm):
    """ 
    Read-only form for displaying slivers in slice admin change form.
    Also it provides popup links to each sliver admin change form.
    """
    #FIXME: js needed: when save popup the main form is not updated with the new/changed slivers
    #TODO: possible reimplementation when nested inlines support becomes available 
    sliver = forms.CharField(label="Sliver", widget=ShowText(bold=True))
    node = forms.CharField(label="Node", widget=ShowText(bold=True))
    cn_url = forms.CharField(label="Node CN URL", widget=ShowText(bold=True))

    class Meta:
        fields = []
    
    def __init__(self, *args, **kwargs):
        super(SliverInlineAdminForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            sliver_change = reverse('admin:slices_sliver_change', args=(instance.pk,))
            node_change = reverse('admin:nodes_node_change', args=(instance.node.pk,))
            self.initial['sliver'] = mark_safe("""<a href='%s' id='add_id_user' 
                onclick='return showAddAnotherPopup(this);'>%s </a>""" % (sliver_change, instance))
            self.initial['node'] = mark_safe("<a href='%s'>%s</a>" % (node_change, instance.node))
            self.initial['cn_url'] = mark_safe("<a href='%s'>%s</a>" % (instance.node.cn_url, 
                instance.node.cn_url))


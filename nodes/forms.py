from django import forms
from slices import models as slice_models
from nodes import models

from nodes import api

from nodes import widgets

class NewSliceForm(forms.Form):
    name = forms.CharField(required = True)
    template = forms.ChoiceField(choices = map(lambda a: [a.id, a.name], slice_models.SliverTemplate.objects.filter(enabled = True)))
    vlan_nr = forms.CharField(required = True)
    exp_data_uri = forms.CharField(required = True)
    exp_data_sha256 = forms.CharField(required = True)
    nodes = forms.MultipleChoiceField(widget=widgets.NodeWithInterfacesWidget)

class NodeForm(forms.ModelForm):    
    class Meta:
        model = models.Node
        
class MemoryForm(forms.ModelForm):    
    class Meta:
        model = models.Memory
        exclude = ('node',)

class StorageForm(forms.ModelForm):    
    class Meta:
        model = models.Storage
        exclude = ('node',)

class CPUForm(forms.ModelForm):    
    class Meta:
        model = models.CPU
        exclude = ('node',)

class InterfaceForm(forms.ModelForm):    
    class Meta:
        model = models.Interface
        exclude = ('node',)
        

class DeleteRequestForm(forms.ModelForm):
    class Meta:
        model = models.DeleteRequest

from django import forms
from nodes import models

from nodes import api

from nodes import widgets

class NewSliceForm(forms.Form):
    name = forms.CharField(required = True)
    nodes = forms.MultipleChoiceField(choices = map(lambda a: [a.id, a.hostname],
                                                    api.get_nodes()),
                                      widget=widgets.NodeWithInterfacesWidget)


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

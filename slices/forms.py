from django import forms
from slices import models

class MemoryRequestForm(forms.ModelForm):    
    class Meta:
        model = models.MemoryRequest
        exclude = ('sliver',)

class StorageRequestForm(forms.ModelForm):    
    class Meta:
        model = models.StorageRequest
        exclude = ('sliver',)

class CPURequestForm(forms.ModelForm):    
    class Meta:
        model = models.CPURequest
        exclude = ('sliver',)

class NetworkRequestForm(forms.ModelForm):    
    class Meta:
        model = models.NetworkRequest
        exclude = ('sliver',)

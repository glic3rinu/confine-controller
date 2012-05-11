from django import forms
from nodes import models

class NewSliceForm(forms.Form):
    name = forms.CharField(required = True)
    nodes = forms.MultipleChoiceField(choices = map(lambda a: [a.id, a.hostname],
                                                    models.Node.objects.all()),
                                      widget=forms.CheckboxSelectMultiple)

class NodeForm(forms.ModelForm):
    class Meta:
        model = models.Node

class DeleteRequestForm(forms.ModelForm):
    class Meta:
        model = models.DeleteRequest

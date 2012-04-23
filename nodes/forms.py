from django import forms
from nodes.models import Node

class NewSliceForm(forms.Form):
    name = forms.CharField()
    nodes = forms.MultipleChoiceField(choices = map(lambda a: [a.id, a.hostname],
                                                    Node.objects.all()),
                                      widget=forms.CheckboxSelectMultiple)

from django import forms

from controller.forms.widgets import ReadOnlyBooleanWidget

from .models import Execution


class ExecutionInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExecutionInlineForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs.get('instance')
            if Execution.objects.filter(created_on__gt=instance.created_on,
                                        operation=instance.operation).exists():
                self.fields['is_active'].widget = ReadOnlyBooleanWidget()
                self.fields['include_new_nodes'].widget = ReadOnlyBooleanWidget()
